import polars as pl

from orca_studio.parse.common import extract_table_lines, find_section_starts

TABLE_HEADER = "IR SPECTRUM"
DATA_OFFSET = 6


def ir_spectrum(lines: list[str]) -> pl.DataFrame:
    section_idx = find_section_starts(lines, TABLE_HEADER)[0]
    table = extract_table_lines(lines, section_idx + DATA_OFFSET)

    data = []
    for row in table:
        tokens = row.strip().replace(":", "").split()
        row_data = dict(
            mode=int(tokens[0]),
            freq=float(tokens[1]),
            eps=float(tokens[2]),
            intensity=float(tokens[3]),
            t2=float(tokens[4]),
        )
        data.append(row_data)
    return pl.DataFrame(data)
