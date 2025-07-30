import numpy as np
import subprocess
import sys

np.set_printoptions(precision=10)
# takes as input an smodes input file and irrep name and creates the distortions needed to do a symmetry adapted modes calculation
# we expect a POSCAR file in this directory to get the header from

dispMag = 0.1
symmPrec = 1e-4  # this is the best smodes can do
# precLatParam=np.array([3.8414838335282817, 3.8414838335282817, 4.7487809860054240])
# precLatParam=np.array([5.4045015262,5.4045015262,5.4045015262])
# precLatParam=np.array([5.4749698639, 5.4749698639, 9.1766004562])

print("!!!!!")
print("REMEMBER TO SET LAT PARAM IN FILE, right now is:")
parentBasis = np.matrix(
    [
        [5.4749698639000002, 0.0000000000000000, 0.0000000000000000],
        [-2.7374849319000001, 4.7414629871000002, 0.0000000000000000],
        [0.0000000000000000, 0.0000000000000000, 9.1766004561999992],
    ]
)
print(parentBasis)
# all this stuff should be extracted in the future but we're cheating now
# find total number of atoms (for now just set it)
numAtoms = 13
typeList = ["Sc", "V", "Sn"]
typeCount = [1, 6, 6]
targetIrrep = "GM6+"
wyckXYZ_i = 0.2480103425295411
wyckXYZ_e = 0.3207760730752693

domainBasis = np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
# domainBasis=np.matrix([[-1,1,0],[-1,-2,0],[0,0,3]])
aPoints = np.matrix([[0.0000000000, 0.0000000000, 0.0000000000]])
iPoints = np.matrix(
    [
        [0.5000000000, 0.0000000000, wyckXYZ_i],
        [0.5000000000, 0.5000000000, wyckXYZ_i],
        [0.0000000000, 0.5000000000, wyckXYZ_i],
        [0.5000000000, 0.0000000000, -wyckXYZ_i],
        [0.5000000000, 0.5000000000, -wyckXYZ_i],
        [0.0000000000, 0.5000000000, -wyckXYZ_i],
    ]
)
ePoints = np.matrix(
    [[0.0000000000, 0.0000000000, wyckXYZ_e], [0.0000000000, 0.0000000000, -wyckXYZ_e]]
)
dPoints = np.matrix(
    [
        [0.3333333333, 0.6666666666, 0.5000000000],
        [-0.3333333333, 0.3333333333, 0.5000000000],
    ]
)
cPoints = np.matrix(
    [
        [0.3333333333, 0.6666666666, 0.0000000000],
        [-0.3333333333, 0.3333333333, 0.0000000000],
    ]
)
newFrac = np.matrix([[0, 0, 0]])
modeTypeList = (
    ["dummy"] + 0 * 2 * ["Sc"] + 2 * 2 * ["V"] + 1 * 2 * ["Sn"]
)  # has to be in order of iso input
print("!!!!!")
isoFile = sys.argv[1]

pointsList = [aPoints, iPoints, ePoints, dPoints, cPoints]
superCell = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        superCell[i, :] = superCell[i, :] + domainBasis[i, j] * parentBasis[j, :]
print(superCell)
# now make all the points with newFrac. Theyre in fractional coordinates of the *parent basis*,
# meaning we need to frac2cart them to cartesian before writing them and looking at them:q


posFracParent = np.zeros((numAtoms, 3))
atomInd = 0
for type in range(len(pointsList)):
    parentSite = pointsList[type]
    shapeSite = parentSite.shape
    for site in range(shapeSite[0]):
        for shift in range(newFrac.shape[0]):
            newPos = parentSite[site, :] + newFrac[shift]
            posFracParent[atomInd, :] = newPos
            atomInd = atomInd + 1
            print(atomInd)
print(posFracParent)
atomCart = np.matmul(posFracParent, parentBasis)
atomFrac = np.matmul(atomCart, np.linalg.inv(superCell))

args = "iso <" + isoFile
# args = 'cat isoout'
proc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
output = proc.stdout.read()
parsedOutput = output.decode("ascii")
outList = parsedOutput.split("\n")

cleanedLines0 = []
for l in range(len(outList)):
    thisLine = outList[l].split()
    if (thisLine[0] == "Enter") and (thisLine[1] == "RETURN"):
        pass
    else:
        cleanedLines0.append(outList[l])
cleanedLines1 = []
lastLine = ""
for l in range(len(cleanedLines0)):
    thisLine = cleanedLines0[l].split()
    if thisLine[-1][-1] == ",":
        lastLine = lastLine + cleanedLines0[l].lstrip(" ")
    else:
        cleanedLines1.append(
            ("".join(lastLine + cleanedLines0[l].lstrip(" "))).replace(",", " ")
        )
        lastLine = ""

wyckDistList = []
thisList = []
thisPosInd = -1
for l in range(len(cleanedLines1)):
    thisLine = cleanedLines1[l].replace(")", ",")
    thisLine = thisLine.replace("(", "")
    thisLine = thisLine.split(",")
    splitSpace = thisLine[0].split()
    if len(splitSpace) > 2:
        if (splitSpace[1] == "Domain") and (splitSpace[2] == "Wyckoff"):
            thisPosInd = thisPosInd + 1
            wyckDistList.append(thisList)
            thisList = []
        elif thisPosInd >= 0:
            thisList.append(thisLine[:-1])
            # print(thisLine)
wyckDistList.append(thisList)
wyckDistList = wyckDistList[1:]
atomIndSamList = []
totalNumOfSam = 0
for w in range(len(wyckDistList)):
    wyckTypeSamList = []
    thisSam = []
    samInd = -1
    for l in range(len(wyckDistList[w])):
        thisLine = wyckDistList[w][l]
        if len(thisLine[0].split()) > 3:
            posLine = [float(i) for i in thisLine[0].split()[3:6]]
            if samInd >= 0:
                wyckTypeSamList.append(thisSam)
            thisSam = []
            samInd = samInd + 1
            totalNumOfSam = totalNumOfSam + 1 * len(thisLine[1:])
        else:
            posLine = [float(i) for i in thisLine[0].split()[0:3]]

        samLine = thisLine[1:]
        posVec = np.array(posLine)
        # now find the atom associated with this
        foundAtom = False
        for atom in range(numAtoms):
            diff = np.sum(np.absolute(posVec - posFracParent[atom, :]))
            if diff < symmPrec:
                foundAtom = True
                thisSam.append([str(atom), samLine])
            # 	print(str(samLine)+"="+str(atom))
        if foundAtom == False:
            print("Couldn't find a match for " + str(posVec) + ", quitting...")
            quit()
    wyckTypeSamList.append(thisSam)
    atomIndSamList.append(wyckTypeSamList)


# now we can finally write the SAM:
allSams = np.zeros(
    (numAtoms, 3, totalNumOfSam + 1)
)  # the first index has no displacement
samInd = 1
for w in range(len(atomIndSamList)):
    for samType in range(len(atomIndSamList[w])):
        numSamAtoms = len(atomIndSamList[w][samType])
        numSams = len(atomIndSamList[w][samType][0][-1])
        # 	numSams=len(atomIndSamList[w][samType])-1
        # 	print(numSams)
        for SAM in range(numSams):
            samMat = np.zeros((numAtoms, 3))
            for atom in range(numSamAtoms):
                # print(atomIndSamList[w][samType][atom][-1][SAM].split())
                thisDist = [
                    float(i) for i in atomIndSamList[w][samType][atom][-1][SAM].split()
                ]
                thisAtom = int(atomIndSamList[w][samType][atom][0])
                samMat[thisAtom, :] = np.array(thisDist)
            # convert them to cartesian using the parentBasis:
            allSams[:, :, samInd] = np.matmul(samMat, parentBasis)
            samInd = samInd + 1
# normalize the SAMs
for m in range(1, totalNumOfSam + 1):
    allSams[:, :, m] = allSams[:, :, m] / np.sqrt(
        np.sum(np.multiply(allSams[:, :, m], allSams[:, :, m]))
    )
    # print(np.sqrt(np.sum(np.multiply(allSams[:,:,m],allSams[:,:,m]))))

# now orthogonalize them
orthMat = np.zeros((numAtoms, 3, totalNumOfSam + 1))
for m in range(1, totalNumOfSam + 1):
    SAM = allSams[:, :, m]
    for n in range(1, m):
        # do gram-schmidt
        SAM = SAM - orthMat[:, :, n] * np.sum(np.multiply(orthMat[:, :, n], SAM))
    # re-normalize
    orthMat[:, :, m] = SAM / np.sqrt(np.sum(np.multiply(SAM, SAM)))
allSams = orthMat

# write header file and displacements
headerName = "headerFile_" + str(targetIrrep) + ".dat"
h = open(headerName, "w")
h.write("Irrep: " + str(targetIrrep) + "\n")
h.close()
h = open(headerName, "a")
h.write("NumSAM: " + str(totalNumOfSam) + "\n")
h.write("NumAtomTypes: " + str(len(typeList)) + "\n")
h.write("NumAtoms: " + str(numAtoms) + "\n")
h.write("DispMag: " + str(dispMag) + "\n")
for i in range(len(typeList)):
    h.write(typeList[i] + " " + str(int(typeCount[i])) + " MASS \n")

# now write all the SAMS to poscars and to the header
for m in range(totalNumOfSam + 1):
    filename = "POSCAR_" + str(targetIrrep) + "_" + str(m)
    # 	thisSamCart=np.matmul(allSams[:,:,m],superCell)
    # 	thisDispCart=atomCart+dispMag*thisSamCart
    # 	thisDispFrac=np.matmul(thisDispCart,np.linalg.inv(superCell))
    thisDispCart = atomCart + dispMag * allSams[:, :, m]
    thisDispFrac = np.matmul(thisDispCart, np.linalg.inv(superCell))
    f = open(filename, "w")
    f.write("Automatically generated with SMODES for irrep " + str(targetIrrep) + "\n")
    f.close()
    f = open(filename, "a")
    f.write("1.0\n")
    for i in range(3):
        for j in range(3):
            f.write("{:.10f}".format(superCell[i, j]) + "\t")
        f.write("\n")
    for i in range(len(typeCount)):
        f.write(str(typeList[i]) + "  ")
    f.write("\n")
    for i in range(len(typeCount)):
        f.write(str(int(typeCount[i])) + "  ")
    f.write("\nDirect\n")

    # we're also going to use this loop to write displacements to the header file
    if m > 0:
        print(m)
        h.write("SAM_" + str(m) + ": " + modeTypeList[m] + "\n")
    for i in range(numAtoms):
        for j in range(3):
            f.write("{:.10f}".format(thisDispFrac[i, j]) + "\t")
            if m > 0:
                h.write("{:.10f}".format(allSams[i, j, m]) + "\t")

        f.write("\n")
        if m > 0:
            h.write("\n")
    f.close()
h.close()
