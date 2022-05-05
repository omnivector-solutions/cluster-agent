_IDENTIFICATION_FLAG = "#SBATCH"
_INLINE_COMMENT_MARK = "#"


def _flagged_line(line: str) -> bool:
    """
    Identify if a provided line starts with the
    identification flag
    """
    return line.startswith(_IDENTIFICATION_FLAG)


def _clean_line(line: str) -> str:
    """
    Clean the provided line by removing the
    identification flag at the beguining of the line,
    then remove the inline comment mark and anything
    after it, and finally strip white spaces at both sides
    """
    return line.lstrip(_IDENTIFICATION_FLAG).split(_INLINE_COMMENT_MARK, 1)[0].strip()


def _clean_jobscript(jobscript: str) -> map:
    """
    Transform a job script string by filtering only the lines that
    start with the identification flag and mapping a cleaning
    procedure to them, in
    order to remove the identification flag, remove inline comments,
    and strip extra white spaces
    """
    jobscript_filtered = filter(_flagged_line, jobscript.split("\n"))
    jobscript_cleaned = map(_clean_line, jobscript_filtered)
    return jobscript_cleaned
