from orca_studio.parse.common import find_keyword_tokens

KEYWORD = "Total entropy correction"
TOKEN_IDX = -4


def entropy_correction_eh(lines: list[str]) -> float:
    tokens = find_keyword_tokens(lines, KEYWORD, TOKEN_IDX)
    return float(tokens[-1])
