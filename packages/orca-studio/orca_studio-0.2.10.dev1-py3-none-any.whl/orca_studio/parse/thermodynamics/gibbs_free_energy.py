from orca_studio.parse.common import find_keyword_tokens

KEYWORD = "Final Gibbs free energy"
TOKEN_IDX = -2


def gibbs_free_energy_eh(lines: list[str]) -> float:
    tokens = find_keyword_tokens(lines, KEYWORD, TOKEN_IDX)
    return float(tokens[-1])
