import re


def format_exception(exc: str) -> str:
    return re.sub(r"^\s*For further information.*(?:\n|$)", "", exc, flags=re.MULTILINE)
