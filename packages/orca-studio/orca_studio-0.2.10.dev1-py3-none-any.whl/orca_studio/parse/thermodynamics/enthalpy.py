from orca_studio.parse.common import find_keyword_tokens

KEYWORD = "Total Enthalpy"
TOKEN_IDX = -2


def enthalpy_eh(lines: list[str]) -> float:
    tokens = find_keyword_tokens(lines, KEYWORD, TOKEN_IDX)
    return float(tokens[-1])
