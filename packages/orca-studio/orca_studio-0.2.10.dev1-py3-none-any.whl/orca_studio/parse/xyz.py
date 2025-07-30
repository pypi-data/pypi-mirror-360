from orca_studio.parse.common import extract_table_lines, find_section_starts

TABLE_HEADER = "CARTESIAN COORDINATES (ANGSTROEM)"
DATA_OFFSET = 2


def xyz(lines: list[str]) -> str:
    """Parse the last cartesian coordinates (angstrom) in the output as a valid XYZ string."""
    section_idx = find_section_starts(lines, TABLE_HEADER)[-1]

    table = extract_table_lines(lines, section_idx + DATA_OFFSET)

    xyz = f"{len(table)}\n\n" + "\n".join(table)
    return xyz
