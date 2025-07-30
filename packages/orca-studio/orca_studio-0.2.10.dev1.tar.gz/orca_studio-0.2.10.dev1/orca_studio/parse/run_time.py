from orca_studio.parse.common import get_line_tokens

KEYWORD = "TOTAL RUN TIME"


def run_time_h(lines: list[str]) -> float:
    tokens = get_line_tokens(lines, KEYWORD)

    # TOTAL RUN TIME: 0 days 1 hours 51 minutes 13 seconds 739 msec
    _, _, _, d, _, h, _, m, _, s, *_ = tokens[-1]
    run_time_h = int(d) * 24 + int(h) + int(m) / 60 + int(s) / 3600
    return round(run_time_h, 2)
