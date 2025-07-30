from orca_studio.parse.common import find_keyword_tokens

KEYWORD = "Number of basis functions"


def basis_functions(lines: list[str]) -> int:
    tokens = find_keyword_tokens(lines, KEYWORD)
    return int(tokens[-1])
