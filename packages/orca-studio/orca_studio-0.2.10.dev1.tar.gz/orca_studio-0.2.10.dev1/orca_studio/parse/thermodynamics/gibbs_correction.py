from orca_studio.parse.common import find_keyword_tokens

KEYWORD = "G-E(el)"
TOKEN_IDX = -4


def gibbs_correction_eh(lines: list[str]) -> float:
    tokens = find_keyword_tokens(lines, KEYWORD, TOKEN_IDX)
    return float(tokens[-1])
