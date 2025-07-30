from orca_studio.parse.common import find_keyword_tokens

KEYWORD = "FINAL SINGLE POINT ENERGY"


def fspe_eh(lines: list[str]) -> float:
    tokens = find_keyword_tokens(lines, KEYWORD)
    return float(tokens[-1])
