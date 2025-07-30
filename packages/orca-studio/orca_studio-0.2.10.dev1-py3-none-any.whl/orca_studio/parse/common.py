from typing import Callable

CONVERSION_TO_HARTREE = {
    "hartree": 1.0,
    "ev": 1.0 / 27.211386,
    "1/cm": 1.0 / 219474.63,
    "kj/mol": 1.0 / 2625.4996,
    "kcal/mol": 1.0 / 627.50947,
}


class OrcaParsingError(Exception):
    """Custom exception for parsing ORCA output files"""

    pass


def find_section_starts(lines: list[str], header_keyword: str, start_offset: int = 0) -> list[int]:
    """Find all starting line numbers of sections containing the header keyword.

    Returns a list of line indices (after apply the offset).
    Raises OrcaParsingError if the header is not found.
    """
    sections = []

    for i, line in enumerate(lines):
        if header_keyword in line.strip():
            sections.append(i + start_offset)

    if len(sections) == 0:
        raise OrcaParsingError(f"Header keyword '{header_keyword}' not found in output")

    return sections


def extract_table_lines(
    all_lines: list[str],
    table_start_index: int,
    end_condition: Callable[[str], bool] = lambda x: not x.strip(),  # Pass current line
    header_rows_to_skip: int = 0,
) -> list[str]:
    """Extracts lines belonging to a table.

    'end_condition' is a callable: 'func(line_content_str) -> bool'
    Defaults to stop on an empty line.
    For example:
    ```py
    def is_end_of_table(line: str) -> bool:
        # End on an empty line
        return not line.strip()
    ```
    """
    table_lines = []

    for i, line in enumerate(all_lines[table_start_index:]):
        if end_condition(line):
            break
        if i >= header_rows_to_skip:
            table_lines.append(line.strip())

    return table_lines


def find_keyword_tokens(lines: list[str], keyword: str, token_idx: int = -1) -> list[str]:
    """Find all starting tokens of lines containing the keyword.

    Returns a list tokens.
    Raises OrcaParsingError if the keyword is not found.
    """
    tokens = []

    for line in lines:
        if keyword in line.strip():
            tokens.append(line.split()[token_idx])

    if len(tokens) == 0:
        raise OrcaParsingError(f"Keyword '{keyword}' not found in output")

    return tokens


def get_line_tokens(lines: list[str], keyword: str) -> list[list[str]]:
    tokens = []

    for line in lines:
        if keyword in line.strip():
            tokens.append(line.split())

    if len(tokens) == 0:
        raise OrcaParsingError(f"Keyword '{keyword}' not found in output")

    return tokens
