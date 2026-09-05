from __future__ import annotations

import os

from .process import available, run


def notify(summary: str, body: str, *, urgency: str = "normal") -> bool:
    if not available("notify-send"):
        return False
    return run(["notify-send", "--app-name=划词翻译", f"--urgency={urgency}", summary, body]).ok


def show_translation(text: str) -> bool:
    if not available("gdbus"):
        return False
    return run(
        [
            "gdbus",
            "call",
            "--session",
            "--dest",
            "io.github.jchou8663.SelectionTranslator",
            "--object-path",
            "/io/github/jchou8663/SelectionTranslator",
            "--method",
            "io.github.jchou8663.SelectionTranslator.Show",
            text,
        ]
    ).ok


def copy(text: str) -> tuple[bool, str]:
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session == "wayland" and available("wl-copy"):
        return run(["wl-copy", "--type", "text/plain;charset=utf-8"], input_text=text).ok, "wl-copy"
    if os.environ.get("DISPLAY") and available("xclip"):
        return run(["xclip", "-selection", "clipboard"], input_text=text).ok, "xclip"
    if os.environ.get("DISPLAY") and available("xsel"):
        return run(["xsel", "--clipboard", "--input"], input_text=text).ok, "xsel"
    if available("copyq"):
        return run(["copyq", "copy", text]).ok, "CopyQ"
    return False, "无可用剪贴板工具"
