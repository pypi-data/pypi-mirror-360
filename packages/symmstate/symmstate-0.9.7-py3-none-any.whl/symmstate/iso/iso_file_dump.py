    def extract_wyckoff_points(self, iso_input_path: str, iso_exe: str = "iso"):
        """
        Run `iso < iso_input_path`, parse its “Dir Domain Wyckoff Point …” blocks, 
        and return a dict mapping each Wyckoff letter ('a','i','d','c',…) to an
        (N×3) NumPy array of fractional coordinates.
        """
        # 1) call iso
        cmd = f"{iso_exe} < {iso_input_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        out = result.stdout

        # 2) regexes
        #   - entry_line picks up lines that introduce a new Wyckoff letter
        entry_line = re.compile(r"^\s*\S+\s+\d+\s+([a-zA-Z])\s*\(")
        #   - coord finds every (x, y, z) in the text
        coord = re.compile(r"\(\s*([-\d\.]+),\s*([-\d\.]+),\s*([-\d\.]+)\)")

        points = defaultdict(list)
        current_letter = None

        for line in out.splitlines():
            m = entry_line.match(line)
            if m:
                # start of a new letter block
                current_letter = m.group(1).lower()   # e.g. 'i', 'd', 'c'
            if current_letter:
                for x,y,z in coord.findall(line):
                    points[current_letter].append([float(x), float(y), float(z)])

        # 3) convert to NumPy arrays
        for letter, lst in points.items():
            points[letter] = np.array(lst)

        return points

    
    def symm_adapt_basis(self, desired_irrep: str, direction: str, disp_mag: float = 0.1) -> Dict[str, Any]:
        """
        Calculate the symmetry adapted basis
        """

        # helper to pretty‐print any matrix
        def _print_matrix(name: str, mat: np.ndarray):
            print(f"{name}:")
            print()
            for row in mat:
                print("   " + "  ".join(f"{x:.10f}" for x in row))
            print()

        np.set_printoptions(precision=10)

        # 1) Parent basis
        parent_basis = self.abi_file.lattice.matrix  # (3×3)
        _print_matrix("Parent basis", parent_basis)

        type_list  = self.abi_file.typat_to_elem()
        natom      = self.abi_file.vars["natom"]
        type_count = self.abi_file.element_multiplicity()

        # 2) Domain & zero‐shift templates
        domain_basis = np.eye(3)            # identity
        new_frac     = np.zeros((1, 3))     # single [0,0,0]

        # 3) Generate and run ISOTROPY to grab the Wyckoff templates
        iso_file = self.write_isotropy_input("iInput.txt",
                                parent_sg, desired_irrep, direction,
                                domain, abc, angles)
        wyck = self.extract_wyckoff_points("iInput.txt")
        # collect in the same order as before:
        point_list = [
            wyck.get("a", np.empty((0, 3))),
            wyck.get("i", np.empty((0, 3))),
            wyck.get("e", np.empty((0, 3))),
            wyck.get("d", np.empty((0, 3))),
            wyck.get("c", np.empty((0, 3))),
        ]

        # 4) Build supercell via NumPy matmul
        super_cell = domain_basis @ parent_basis
        _print_matrix("Supercell", super_cell)

        # 5) Generate parent fractional positions with a comprehension
        post_frac_parent = np.vstack(
            site + shift
            for pts in point_list
            for site in pts
            for shift in new_frac
        )
        _print_matrix("Post parent structure", post_frac_parent)

        # 6) Convert to Cartesian & then back to fractional in the supercell
        atom_cart = post_frac_parent @ parent_basis
        atom_frac = atom_cart @ np.linalg.inv(super_cell)

        # 7) Run ISOTROPY again for the distortion modes (unchanged)
        result = subprocess.run(
            ["iso", "<", iso_file],
            shell=True,
            capture_output=True,
            text=True,
        )
        output  = result.stdout.strip().splitlines()

        # 8) Clean and parse the raw output (same logic as before)
        cleaned_lines0 = []
        for line in output:
            parts = line.split()
            if not (parts and parts[0] == "Enter" and parts[1] == "RETURN"):
                cleaned_lines0.append(line)

        cleaned_lines1 = []
        last = ""
        for line in cleaned_lines0:
            parts = line.split()
            if parts[-1].endswith(","):
                last += line.lstrip()
            else:
                combined = (last + line.lstrip()).replace(",", " ")
                cleaned_lines1.append(combined)
                last = ""

        # 9) Build the wyckoff‐distance list, sample indices, etc.
        wyck_dist_list = []
        this_list = []
        pos_idx = -1
        for entry in cleaned_lines1:
            entry = entry.replace(")", ",").replace("(", "")
            cols  = entry.split(",")
            head  = cols[0].split()
            if len(head) > 2 and head[1] == "Domain" and head[2] == "Wyckoff":
                pos_idx += 1
                wyck_dist_list.append(this_list)
                this_list = []
            elif pos_idx >= 0:
                this_list.append(this_list[:-1])
        wyck_dist_list.append(this_list)
        wyck_dist_list = wyck_dist_list[1:]

        # 10) Assemble per‐mode atom‐index & displacement‐string lists
        atom_ind_sam_list = []
        total_nsams = 0
        for block in wyck_dist_list:
            type_list_block = []
            this_sam        = []
            sam_idx         = -1
            for segment in block:
                # ... same splitting into pos_line, sam_line, matching to post_frac_parent ...
                # update total_nsams accordingly
                pass
            atom_ind_sam_list.append(type_list_block)

        # 11) Build all_sams array via NumPy & then normalize each mode
        all_sams = np.zeros((natom, 3, total_nsams + 1))
        sam_counter = 1
        for wblock in atom_ind_sam_list:
            for sam_type in wblock:
                # ← Here is where you need to initialize sam_mat:
                sam_mat = np.zeros((natom, 3))
                # Then, for each atom in this mode:
                for atom_idx, sam_lines in sam_type:
                    # sam_lines is the list of string displacements for this atom
                    # e.g. ["0.123", "-0.045", "0.000"]
                    this_dist = np.array([float(x) for x in sam_lines[sam_counter-1].split()])
                    sam_mat[atom_idx, :] = this_dist
                # once sam_mat is filled, convert to Cartesian:
                all_sams[:, :, sam_counter] = sam_mat @ parent_basis
                sam_counter += 1

        # 12) Orthonormalize via Gram–Schmidt (using enumerate)
        orthogonal = np.zeros_like(all_sams)
        for m, vec in enumerate(all_sams[..., 1:], start=1):
            v = vec.copy()
            for n, prev in enumerate(orthogonal[..., 1:m], start=1):
                v -= prev * np.tensordot(prev, vec, axes=([0, 1], [0, 1]))
            orthogonal[..., m] = v / np.linalg.norm(v)
        all_sams = orthogonal

        # 13) Package results and return
        return {
            "irrep": desired_irrep,
            "direction": direction,
            "disp_mag": disp_mag,
            "num_sams": total_nsams,
            "type_list": type_list,
            "type_count": type_count,
            "natom": natom,
            "parent_basis": parent_basis,
            "super_cell": super_cell,
            "atom_cart": atom_cart,
            "all_sams": all_sams,
        }






import numpy as np
import sys

# ----------------------------------------------------------
# 1) Run the symmetry‐adapt routine and grab its outputs
# ----------------------------------------------------------
target_irrep = sys.argv[1]
# assume `obj` is an instance of the class that defines symm_adapt_basis
data = obj.symm_adapt_basis(target_irrep, direction="C1", disp_mag=0.1)

# ----------------------------------------------------------
# 2) Unpack everything you need
# ----------------------------------------------------------
Irrep         = data["irrep"]
NumSAM        = data["num_sams"]
typeList      = data["type_list"]
typeCount     = data["type_count"]
NumAtomTypes  = len(typeList)
NumAtoms      = data["natom"]
DispMag       = data["disp_mag"]
SAMmat        = data["all_sams"]       # shape = (NumAtoms, 3, NumSAM+1)
SAMatomLabel  = data["mode_labels"]    # length = NumSAM+1
atom_cart     = data["atom_cart"]      # (NumAtoms, 3)
super_cell    = data["super_cell"]     # (3,3)

print(f"Irrep:       {Irrep}")
print(f"NumSAM:      {NumSAM}")
print(f"NumAtomTypes:{NumAtomTypes}")
print(f"NumAtoms:    {NumAtoms}")
print(f"DispMag:     {DispMag:.6f}\n")

# ----------------------------------------------------------
# 3) If you need masses, you can still build them here
# ----------------------------------------------------------
# (You’ll need a mapping from element symbol → mass, e.g. via pymatgen:
from pymatgen.core.periodic_table import Element
massList = [ Element(sym).atomic_mass for sym in typeList ]

print("Unit cell consists of " +
      ", ".join(f"{c}×{s} (mass={m:.3f} amu)"
                for s, c, m in zip(typeList, typeCount, massList))
      + "\n")

# ----------------------------------------------------------
# 4) Build your force‐constant matrix exactly as before
# ----------------------------------------------------------
# (You still loop over the OUTCARs etc.; that part is unchanged.)
# For brevity I’ll just show you skipping the “read header” and 
# going straight to the part where you subtract the reference forces:
forceMat_raw = np.zeros((NumAtoms, 3, NumSAM+1))
for sam in range(NumSAM+1):
    path = f"ISO_{Irrep}/dist_{sam}/OUTCAR"
    with open(path) as f:
        lines = f.readlines()
    # find the “POSITION TOTAL‐FORCE” block
    for i, L in enumerate(lines):
        if L.startswith("POSITION") and "TOTAL-FORCE" in L:
            start = i+2
            break
    for atom in range(NumAtoms):
        vals = lines[start+atom].split()
        forceMat_raw[atom, :, sam] = [float(vals[3]), float(vals[4]), float(vals[5])]

# subtract off the zero‐displacement forces
forceList = forceMat_raw[:, :, 1:] - forceMat_raw[:, :, [0]]

# build the force‐constant matrix
forceMat = np.zeros((NumSAM, NumSAM))
# drop the zero‐mode from SAMmat
SAMmat = SAMmat[:, :, 1:]
for f in range(NumSAM):
    for s in range(NumSAM):
        forceMat[f, s] = (forceList[:, :, f] * SAMmat[:, :, s]).sum()

# build the mass‐matrix
massVec = np.array([ massList[typeList.index(lbl)] for lbl in SAMatomLabel[1:] ])
MM = np.sqrt(np.outer(massVec, massVec))

# now FC_mat, Dyn_mat, eigen‐stuff, etc. is exactly as before
FC_mat     = -forceMat / DispMag
FC_mat     = (FC_mat + FC_mat.T) / 2.0
Dyn_mat    = FC_mat / MM
FCevals,  FCevecs_SAM  = np.linalg.eig(FC_mat)
Dynevals, Dynevecs_SAM = np.linalg.eig(Dyn_mat)

# …and so on with your frequency conversion and real‐space reconstruction…

# ----------------------------------------------------------
# After: FC_mat, Dyn_mat, FCevals, FCevecs_SAM,
#        Dynevals, Dynevecs_SAM  (SCALAR and SAM‐BASIS eigenpairs)
# ----------------------------------------------------------

# 1) Convert eigenvalues → phonon frequencies
eV_to_J       = 1.602177e-19
angstrom_to_m = 1e-10
amu_to_kg     = 1.66053e-27
c_cm          = 2.9979458e10   # speed of light in cm/s

# compute ω (in 2π THz)
omega_2pi_THz = np.sign(Dynevals) * np.sqrt(
    np.abs(Dynevals) * eV_to_J
    / (angstrom_to_m**2 * amu_to_kg)
) * 1e-12

# convert to THz
omega_THz = omega_2pi_THz / (2 * np.pi)

# convert to cm⁻¹
freq_cm = omega_THz * 1e12 / c_cm

# sort descending by frequency
idx = np.argsort(omega_THz)[::-1]
omega_THz = omega_THz[idx]
freq_cm    = freq_cm[idx]

# reorder eigenvectors accordingly
Dynevecs_SAM = Dynevecs_SAM[:, idx]
FCevals      = FCevals[idx]
FCevecs_SAM  = FCevecs_SAM[:, idx]

# ----------------------------------------------------------
# 2) Reconstruct real‐space eigenvectors from the SAM basis
#     Dynevecs_SAM: shape (NumSAM, NumSAM)
#     SAMmat:       shape (NumAtoms, 3, NumSAM+1) – drop index 0
# ----------------------------------------------------------
NumModes = NumSAM
SAM_modes = SAMmat[:, :, 1:]  # now shape (NumAtoms,3,NumModes)

# initialize real‐space arrays
Dynevecs_real = np.zeros((NumAtoms, 3, NumModes))
FCEvecs_real  = np.zeros((NumAtoms, 3, NumModes))

for m in range(NumModes):
    # the m-th phonon eigenvector in the SAM basis:
    e_dyn = Dynevecs_SAM[:, m]   # length NumModes
    e_fc  = FCevecs_SAM[:, m]

    # sum over SAMs to build the real‐space displacement for each atom
    for s in range(NumModes):
        Dynevecs_real[:, :, m] += e_dyn[s] * SAM_modes[:, :, s]
        FCEvecs_real[:, :, m]  += e_fc[s]  * SAM_modes[:, :, s]

# ----------------------------------------------------------
# 3) Build mass‐weighted phonon displacement eigenvectors & reduced masses
# ----------------------------------------------------------
# get per‐atom masses (in kg) from atomic symbol list
from pymatgen.core.periodic_table import Element
atom_symbols = []   # fill this from your structure, e.g. self.abi_file.typat_to_elem()
for sym in atom_symbols:
    atom_m = Element(sym).atomic_mass * amu_to_kg
    atom_symbols.append(sym)

MassCol = np.array([Element(sym).atomic_mass * amu_to_kg
                    for sym in atom_symbols])  # shape (NumAtoms,)

PhonDispEigs = np.zeros_like(Dynevecs_real)
redmass      = np.zeros(NumModes)

for m in range(NumModes):
    # mass‐weight
    PhonDispEigs[:, :, m] = Dynevecs_real[:, :, m] / MassCol[:, None]
    # compute reduced mass = 1 / ||u||²
    norm_sq = np.sum(PhonDispEigs[:, :, m]**2)
    redmass[m] = 1.0 / norm_sq
    # normalize the displacement eigenvector
    PhonDispEigs[:, :, m] /= np.sqrt(norm_sq)

# ----------------------------------------------------------
# Now you have:
#   omega_THz   – sorted phonon freqs in THz
#   freq_cm     – sorted freqs in cm⁻¹
#   Dynevecs_real – (NumAtoms,3,NumModes) real‐space phonon modes
#   redmass     – reduced masses for each mode
#   FCEvecs_real  – (NumAtoms,3,NumModes) FC eigenvectors in real space
# ----------------------------------------------------------

# From here you can write them out, plot them, or return them to the caller.
