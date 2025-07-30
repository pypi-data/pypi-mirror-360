from orca_studio.parse.common import find_keyword_tokens

KEYWORD = "Tamm-Dancoff approximation     ... "


def tda(lines: list[str]) -> bool:
    tokens = find_keyword_tokens(lines, KEYWORD)
    if tokens[-1] == "deactivated":
        return False
    else:
        return True
