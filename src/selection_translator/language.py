from __future__ import annotations

import re

_CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
_LATIN = re.compile(r"[A-Za-z]")


def translation_direction(text: str) -> tuple[str, str]:
    """Choose Chinese->English if CJK is at least half of CJK/Latin letters."""
    cjk = len(_CJK.findall(text))
    latin = len(_LATIN.findall(text))
    return ("zh", "en") if cjk and cjk >= latin else ("en", "zh")

