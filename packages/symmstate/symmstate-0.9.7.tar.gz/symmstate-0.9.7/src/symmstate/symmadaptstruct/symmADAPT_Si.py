import phonopy
from phonopy.phonon.band_structure import get_band_qpoints_and_path_connections
import plotly.graph_objects as go
import numpy as np


def find_irrep():
    return "irrep_placeholder"


def find_degeneracy():
    return 1


# Define your path and labels
path = [
    [[0, 0, 0], [0.375, 0.375, 0.75], [0.5, 0.0, 0.5], [0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]
]
labels = ["G", "K", "X", "G", "L"]

qpoints, connections = get_band_qpoints_and_path_connections(path, npoints=51)
phonon = phonopy.load("phonopy_params.yaml")
phonon.run_band_structure(qpoints, path_connections=connections, labels=labels)

bs = phonon.band_structure
fig = go.Figure()

for i, (d, f) in enumerate(zip(bs.distances, bs.frequencies)):
    for j, band in enumerate(f.T):
        # Example: set degeneracy to 8 for the first trace, otherwise 1
        if i == 2:
            if j == 1:
                degeneracy = 12
                irrep = "DT5"
            if j == 2:
                degeneracy = 6
                irrep = "DT3"
            if j == 3:
                degeneracy = 6
                irrep = "DT1"
            if j == 4:
                degeneracy = 12
                irrep = "DT5"
            if j == 5:
                degeneracy = 6
                irrep = "DT1"
        elif i == 3:
            if j == 1:
                degeneracy = 16
                irrep = "LD3"
            elif j == 2:
                degeneracy = 8
                irrep = "LD1"
            elif j == 3:
                degeneracy = 16
                irrep = "LD3"
            elif j == 5:
                degeneracy = 8
                irrep = "LD1"
        else:
            degeneracy = "undefined"
            irrep = "undefined"
        degeneracy_arr = [degeneracy] * len(d)
        irrep_arr = [irrep] * len(d)
        customdata = np.stack((d, band, irrep_arr, degeneracy_arr), axis=-1)
        fig.add_trace(
            go.Scatter(
                x=d,
                y=band,
                mode="lines",
                name=f"Band {i}-{j}",  # set the trace name
                customdata=customdata,
                hovertemplate=(
                    "f: %{customdata[1]:.3f} THz<br>"
                    "Symmetry: %{customdata[2]}<br>"
                    "Degeneracy: %{customdata[3]}<extra></extra>"
                ),
            )
        )

# The first point of each segment is a high-symmetry point
label_positions = [d[0] for d in bs.distances]
label_names = [l[0] for l in bs.labels]
if bs.labels[-1][-1] is not None:
    label_positions.append(bs.distances[-1][-1])
    label_names.append(bs.labels[-1][-1])

for pos in label_positions:
    fig.add_vline(x=pos, line=dict(color="black", width=1, dash="dash"))


fig.update_layout(
    xaxis=dict(
        title="Wave Vector",
        tickmode="array",
        tickvals=label_positions,
        ticktext=label_names,
    ),
    yaxis_title="Frequency (THz)",
    title="Phonon Dispersion Curve of Si 227",
)


# Add special points at label positions
for label_x, label_name in zip(label_positions, label_names):
    for d, f in zip(bs.distances, bs.frequencies):
        for band in f.T:
            # Interpolate y at label_x if label_x is within d
            if label_x >= d[0] and label_x <= d[-1]:
                y_interp = np.interp(label_x, d, band)
                if label_name == "G":
                    if (
                        y_interp == 2.8016395287881164e-07
                        or y_interp == 2.0472198329825477e-07
                        or y_interp == -1.213302824223871e-07
                    ):
                        irrep = "GM4-"
                        degeneracy = 3
                    if (
                        y_interp == 15.287177002895199
                        or y_interp == 15.287177002895202
                        or y_interp == 15.287177002895204
                    ):
                        irrep = "GM5+"
                        degeneracy = 3
                elif label_name == "L":
                    if y_interp == 3.1013425020653322 or y_interp == 3.1013425020653456:
                        irrep = "L3+"
                        degeneracy = 8
                    if y_interp == 11.080257458995055:
                        irrep = "L2-"
                        degeneracy = 4
                    if y_interp == 12.26800790823089:
                        irrep = "L1+"
                        degeneracy = 4
                    if y_interp == 14.568775210472637 or y_interp == 14.56877521047264:
                        irrep = "L3-"
                        degeneracy = 8
                elif label_name == "X":
                    if y_interp == 3.9831349020029334 or y_interp == 3.983134902002938:
                        irrep = "X4"
                        degeneracy = 6
                    if y_interp == 12.141097662560089 or y_interp == 12.141097662560094:
                        irrep = "X1"
                        degeneracy = 6
                    if y_interp == 13.724739202054431 or y_interp == 13.724739202054433:
                        irrep = "X3"
                        degeneracy = 6
                else:
                    irrep = "Undefined"
                    degeneracy = "Undefined"

                degeneracy_arr = [degeneracy] * len(d)
                irrep_arr = [irrep] * len(d)
                y_interp_arr = [y_interp] * len(d)
                customdata = np.stack(
                    (irrep_arr, y_interp_arr, degeneracy_arr), axis=-1
                )
                fig.add_trace(
                    go.Scatter(
                        x=[label_x],
                        y=[y_interp],
                        mode="markers",
                        marker=dict(color="black", size=8, symbol="diamond"),
                        showlegend=False,
                        customdata=np.array(
                            [[irrep, y_interp, degeneracy]]
                        ),  # shape (1, 3)
                        hovertemplate=(
                            "f: %{customdata[1]:.3f} THz<br>"
                            "Symmetry: %{customdata[0]}<br>"
                            "Degeneracy: %{customdata[2]}<extra></extra>"
                        ),
                    )
                )

fig.write_html("phonon_dispersion.html")
print("Plot saved as phonon_dispersion.html. Open this file in your browser.")
