from orca_studio.parse.common import find_keyword_tokens

KEYWORD = "Zero point energy"
TOKEN_IDX = -4


def zero_point_energy_eh(lines: list[str]) -> float:
    tokens = find_keyword_tokens(lines, KEYWORD, TOKEN_IDX)
    return float(tokens[-1])
