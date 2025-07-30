from orca_studio.parse.common import find_keyword_tokens

KEYWORD = "Multiplicity           Mult"


def mult(lines: list[str]) -> int:
    tokens = find_keyword_tokens(lines, KEYWORD)
    return int(tokens[-1])
