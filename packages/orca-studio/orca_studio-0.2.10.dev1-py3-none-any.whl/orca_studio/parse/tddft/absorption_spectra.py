import polars as pl

from orca_studio.parse.common import extract_table_lines, find_section_starts


def absorption_spectrum(lines: list[str]) -> pl.DataFrame:
    TABLE_HEADER = "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS"
    DATA_OFFSET = 5
    # This also catches the "SOC CORRECTED {TABLE_HEADER}",
    # so use the first occurence - but what if multiple
    # absorption spectra are printed in one output file?
    # Return a list of all?
    section_idx = find_section_starts(lines, TABLE_HEADER)[0]
    table = extract_table_lines(lines, section_idx + DATA_OFFSET)

    def parse_transition(transition: str):
        tokens = transition.split("-")
        id = int(tokens[0])
        # strip symmetry label
        mult = int(tokens[1][:-1])
        return id, mult

    data = []
    for row in table:
        tokens = row.strip().split()
        row_data = dict(
            from_id=parse_transition(tokens[0])[0],
            from_mult=parse_transition(tokens[0])[1],
            to_id=parse_transition(tokens[2])[0],
            to_mult=parse_transition(tokens[2])[1],
            energy_ev=float(tokens[3]),
            energy_cm=float(tokens[4]),
            wavelength_nm=float(tokens[5]),
            fosc=float(tokens[6]),
        )
        data.append(row_data)
    return pl.DataFrame(data)


def soc_absorption_spectrum(lines: list[str]) -> pl.DataFrame:
    TABLE_HEADER = (
        "SOC CORRECTED ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS"
    )
    DATA_OFFSET = 5
    # This also catches the "SOC CORRECTED {TABLE_HEADER}",
    # so use the first occurence - but what if multiple
    # absorption spectra are printed in one output file?
    # Return a list of all?
    section_idx = find_section_starts(lines, TABLE_HEADER)[0]
    table = extract_table_lines(lines, section_idx + DATA_OFFSET)

    def parse_transition(transition: str):
        tokens = transition.split("-")
        id = int(tokens[0])
        # strip symmetry label
        mult = int(tokens[1][:-1])
        return id, mult

    data = []
    for row in table:
        tokens = row.strip().split()
        row_data = dict(
            from_id=parse_transition(tokens[0])[0],
            from_mult=parse_transition(tokens[0])[1],
            to_id=parse_transition(tokens[2])[0],
            to_mult=parse_transition(tokens[2])[1],
            energy_ev=float(tokens[3]),
            energy_cm=float(tokens[4]),
            wavelength_nm=float(tokens[5]),
            fosc=float(tokens[6]),
        )
        data.append(row_data)
    return pl.DataFrame(data)
