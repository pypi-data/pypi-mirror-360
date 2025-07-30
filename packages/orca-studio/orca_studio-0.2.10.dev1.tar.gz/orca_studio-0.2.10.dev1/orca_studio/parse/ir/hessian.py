import polars as pl

from orca_studio.parse.common import extract_table_lines, find_section_starts

TABLE_HEADER = "$hessian"
DATA_OFFSET = 2


def hessian(lines: list[str]) -> pl.DataFrame:
    section_idx = find_section_starts(lines, TABLE_HEADER)[-1]
    dimension = int(lines[section_idx + 1])
    table = extract_table_lines(lines, section_idx + DATA_OFFSET)

    chunk_size = dimension + 1
    chunks = [table[i : i + chunk_size] for i in range(0, len(table), chunk_size)]

    # turn each block into its own DataFrame
    block_dfs = []
    for chunk in chunks:
        # first line of chunk are the global column indices for this block
        col_names = chunk[0].split()
        # remaining lines are rows: drop the row-index token, parse floats
        rows = [[float(tok) for tok in row.split()[1:]] for row in chunk[1:]]
        block_dfs.append(pl.DataFrame(rows, schema=col_names, orient="row"))

    # horizontally stitch all blocks together along their shared row-axis
    # pl.concat with how="horizontal" keeps row order
    df = pl.concat(block_dfs, how="horizontal")
    return df
