import marimo

__generated_with = "0.13.14"
app = marimo.App(width="full")


@app.cell
def _():
    import sys
    from pathlib import Path

    import marimo as mo
    import polars as pl

    from orca_studio import Molecule, OrcaOutput, Renderer
    from orca_studio.apps.plots import broadened_absorption_spectrum

    return (
        Molecule,
        OrcaOutput,
        Path,
        Renderer,
        broadened_absorption_spectrum,
        mo,
        pl,
        sys,
    )


@app.cell
def _(Path, mo, sys):
    # Output file input

    # Check for command line argument
    _arg = sys.argv[-1]
    if _arg.endswith(".out"):
        _default = Path(_arg)
    else:
        _default = ""

    # Create a text input for the ORCA output file
    output_file_input = mo.ui.text(
        label="ORCA output file input",
        value=_default,
        placeholder="Enter the path to the output file",
        full_width=True,
    ).form()
    output_file_input
    return (output_file_input,)


@app.cell
def _(Molecule, OrcaOutput, Path, mo, output_file_input):
    # Validate ORCA output file path
    mo.stop(
        not output_file_input.value, "Please provide a valid ORCA output file path."
    )
    output_file = Path(output_file_input.value)
    if not output_file.exists():
        mo.stop(True, f"The file '{output_file}' does not exist.")

    # Define global variables
    data = OrcaOutput(output_file)
    mol = Molecule.from_output(output_file)
    return data, mol, output_file


@app.cell
def _(energy_unit_radio, mo):
    _unit = energy_unit_radio.value

    _units = {
        "energy_cm": dict(
            label="FWHM (1/cm)",
            start=1,
            stop=5000,
            value=2000,
            step=10,
        ),
        "wavelength_nm": dict(
            label="FWHM (nm)",
            start=1,
            stop=100,
            value=20,
            step=1,
        ),
    }

    fwhm_number = mo.ui.slider(
        **_units[_unit],
        show_value=True,
        debounce=True,
        full_width=True,
    )
    fwhm_number
    return (fwhm_number,)


@app.cell
def _(mo):
    energy_unit_radio = mo.ui.radio(
        options={
            "Wavenumber (1/cm)": "energy_cm",
            "Wavelength (nm)": "wavelength_nm",
        },
        value="Wavenumber (1/cm)",
        label="Energy unit",
    )
    energy_unit_radio
    return (energy_unit_radio,)


@app.cell
def _(mo):
    show_state_numbers = mo.ui.switch(label="Show state numbers", value=True)
    show_state_numbers
    return (show_state_numbers,)


@app.cell
def _(data):
    data.absorption_spectrum
    return


@app.cell
def _(mo):
    do_soc = mo.ui.switch(label="Show SOC states", value=False)
    do_soc
    return (do_soc,)


@app.cell
def _(
    broadened_absorption_spectrum,
    data,
    do_soc,
    energy_unit_radio,
    fwhm_number,
    mo,
    output_file,
    pl,
    show_state_numbers,
):
    def create_fig():
        _unit = energy_unit_radio.value

        _units = {
            "energy_cm": dict(energy_column="energy_cm", grid_domain=[0, 60_000]),
            "wavelength_nm": dict(
                energy_column="wavelength_nm", grid_domain=[200, 800]
            ),
        }

        _spectrum = (
            data.absorption_spectrum
            if do_soc.value is False
            else data.soc_absorption_spectrum
        )
        # _spectrum = data.absorption_spectrum

        _spectrum = _spectrum.with_columns(
            pl.when(pl.col("to_mult") == 1)
            .then(pl.lit("S") + pl.col("to_id").cast(str))
            .when(pl.col("to_mult") == 3)
            .then(pl.lit("T") + pl.col("to_id").cast(str))
            .otherwise(pl.col("to_id").cast(str))
            .alias("label")
        )

        _fig = broadened_absorption_spectrum(
            _spectrum,
            fwhm=fwhm_number.value,
            name_column="label",
            **_units[_unit],
        )

        _input_str = output_file.with_suffix(".inp").read_text()
        _geom_part = _input_str.index("*")

        input_tokens = _input_str[:_geom_part]

        _fig.update_layout(
            title=dict(
                text="TDDFT Absorption Spectrum"
                if do_soc.value is False
                else "SOC-TDDFT Absorption Spectrum",
                subtitle=dict(
                    text=input_tokens,
                    font=dict(color="gray", size=13),
                ),
            ),
            template="plotly_white",  # or "ggplot2", "seaborn", etc.
            width=720,
            height=480,
            showlegend=False,
            xaxis_title="Wavelength (nm)"
            if _unit == "wavelength_nm"
            else "Energy (1/cm)",
            yaxis_title="Intensity (a.u.)",
            font=dict(size=16),  # overall font size
            title_font=dict(size=20, family="Arial", color="black"),  # optional
            xaxis=dict(
                title_font=dict(size=22, family="Arial", color="black"),
                tickfont=dict(size=20),
                mirror=True,
                ticks="outside",
                showline=True,
                linewidth=2,
                linecolor="black",
            ),
            yaxis=dict(
                title_font=dict(size=22, family="Arial", color="black"),
                tickfont=dict(size=20),
                showline=True,
                mirror=True,
                ticks="outside",
                linewidth=2,
                linecolor="black",
            ),
        )

        if not show_state_numbers.value:
            _fig.data[-1].visible = False

        fig_data = _fig

        fig = mo.ui.plotly(_fig)
        return fig

    return (create_fig,)


@app.cell
def _(create_fig):
    fig = create_fig()
    fig
    return (fig,)


@app.cell
def _(mo, output_file):
    _input_str = output_file.with_suffix(".inp").read_text()
    _geom_part = _input_str.index("*")

    mo.md(f"{_input_str[:_geom_part]}")
    return


@app.cell
def _(mo, output_file):
    write_image_path = mo.ui.text(
        label="Write image to",
        value=str(output_file.with_suffix(".svg")),
        full_width=True,
    )
    write_image_button = mo.ui.run_button(label="Write image", full_width=True)
    mo.vstack([write_image_path, write_image_button])
    return write_image_button, write_image_path


@app.cell
def _(fig_data, mo, write_image_button, write_image_path):
    mo.stop(not write_image_button.value)

    fig_data.write_image(
        write_image_path.value,
        format="svg",
        scale=2,
    )
    return


@app.cell
def _(data, fig, mo, pl):
    _idx = [i + 1 for i in fig.indices]

    if _idx:
        _df = data.absorption_spectrum.filter(pl.col("to_id").is_in(_idx))
    else:
        _df = data.absorption_spectrum

    _df = _df.drop(["from_id", "from_id"])
    states = mo.ui.table(
        _df,
        selection="single",
        page_size=20,
        format_mapping={
            "wavelength_nm": "{:.0f}",
            "energy_cm": "{:.0f}",
            "energy_ev": "{:.2f}",
            "fosc": "{:.3f}",
        },
    )
    states
    return (states,)


@app.cell
def _(mo):
    # Isovalue radio
    iso = mo.ui.radio(
        label="Isovalue",
        value="0.0025",
        options={
            "0.1000": 0.1,
            "0.0500": 0.05,
            "0.0250": 0.025,
            "0.0025": 0.0025,
            "0.0010": 0.001,
        },
    )
    iso
    return (iso,)


@app.cell
def _():
    # gbw_file = output_file.with_suffix(".gbw")

    # def render_difference_density(state: pl.DataFrame) -> mo.vstack:
    #     id = selected_states.value["to_state"].item()
    #     mult = selected_states.value["to_mult"].item()

    #     triplet = True if mult == 3 else False

    #     with mo.status.spinner(title="Rendering difference density..") as _spinner:
    #         _dd_file = mol.create_difference_density(
    #             gbw_file, data.get_state_vector(state, triplet)
    #         )
    #     _fig = mol.create_fig_with_isosurface(
    #         _dd_file, isovalue=iso.value, colors=("#CCBE00", "#CC0022")
    #     )

    #     mo.vstack([_fig, _dd_file])
    return


@app.cell
def _(mo):
    grid_selector = mo.ui.radio(
        label="Grid size", options={"40": 40, "60": 60, "100": 100}, value="60"
    )
    grid_selector
    return (grid_selector,)


@app.cell
def _(Renderer, data, grid_selector, iso, mo, mol, output_file, states):
    gbw_file = output_file.with_suffix(".gbw")

    if states.value.is_empty():
        state = None
        mult = None
    else:
        state = states.value["to_id"].item()
        mult = states.value["to_mult"].item()
        triplet = True if mult == 3 else False

    _dd_file = ""
    renderer = Renderer(output_file)

    if state:
        with mo.status.spinner(title="Rendering difference density..") as _spinner:
            _dd_file = mol.create_difference_density(
                gbw_file,
                data.get_state_vector(state, triplet),
                grid=grid_selector.value,
            )
        _fig = mol.create_fig_with_isosurface(
            _dd_file, isovalue=iso.value, colors=("#CCBE00", "#CC0022")
        )

    mo.vstack([renderer.fig, _dd_file])
    return gbw_file, mult, state


@app.cell
def _(data, mo, mult, pl, state):
    mo.stop(state is None or mult == 3)

    root_df = mo.ui.table(
        data.excited_states.filter(pl.col("state_id") == state)
        .select(
            pl.col("from_orb"),
            pl.col("to_orb"),
            pl.col("weight").round(2),
        )
        .sort(by="weight", descending=True),
        selection="single",
    )
    root_df
    return (root_df,)


@app.cell
def _(gbw_file, mo, mol, root_df):
    mo.stop(root_df.value.is_empty())

    orbs = (root_df.value["from_orb"].item(), root_df.value["to_orb"].item())
    with mo.status.spinner(title="Rendering molecular orbitals..") as _spinner:
        from_orb = mol.create_molecular_orbital(gbw_file, orbs[0])
        to_orb = mol.create_molecular_orbital(gbw_file, orbs[1])
    _fig_from = mol.create_fig_with_isosurface(from_orb, isovalue=0.05)
    _fig_to = mol.create_fig_with_isosurface(to_orb, isovalue=0.05)
    mo.hstack([_fig_from, _fig_to])
    return


if __name__ == "__main__":
    app.run()
