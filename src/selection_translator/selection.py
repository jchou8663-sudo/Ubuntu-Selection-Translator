from __future__ import annotations

import os
from dataclasses import dataclass

from .process import available, run


@dataclass(frozen=True)
class Selection:
    text: str
    source: str


def _clean(value: str) -> str:
    return value.replace("\x00", "").strip()


def _command_selection(command: list[str], source: str) -> Selection | None:
    result = run(command)
    text = _clean(result.stdout) if result.ok else ""
    return Selection(text, source) if text else None


def _atspi_selection() -> Selection | None:
    """Best-effort focused-object query; many apps do not expose AT-SPI text."""
    try:
        import pyatspi  # type: ignore[import-not-found]
    except (ImportError, RuntimeError):
        return None

    def visit(node: object, depth: int = 0) -> str:
        if depth > 12:
            return ""
        try:
            states = node.getState()  # type: ignore[attr-defined]
            if states.contains(pyatspi.STATE_FOCUSED):
                try:
                    text = node.queryText()  # type: ignore[attr-defined]
                    if text.getNSelections() > 0:
                        start, end = text.getSelection(0)
                        return _clean(text.getText(start, end))
                except (NotImplementedError, LookupError, RuntimeError):
                    pass
            for child in node:  # type: ignore[union-attr]
                found = visit(child, depth + 1)
                if found:
                    return found
        except (LookupError, RuntimeError):
            return ""
        return ""

    try:
        text = visit(pyatspi.Registry.getDesktop(0))
    except (LookupError, RuntimeError):
        return None
    return Selection(text, "AT-SPI 聚焦选区") if text else None


def get_selection() -> Selection | None:
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    candidates: list[tuple[list[str], str]] = []
    if session == "wayland" and available("wl-paste"):
        candidates.append((["wl-paste", "--primary", "--no-newline"], "Wayland PRIMARY"))
    if os.environ.get("DISPLAY"):
        if available("xclip"):
            candidates.append((["xclip", "-o", "-selection", "primary"], "X11 PRIMARY"))
        elif available("xsel"):
            candidates.append((["xsel", "--primary", "--output"], "X11 PRIMARY"))
    for command, source in candidates:
        selected = _command_selection(command, source)
        if selected:
            return selected
    selected = _atspi_selection()
    if selected:
        return selected
    clipboard: list[tuple[list[str], str]] = []
    if session == "wayland" and available("wl-paste"):
        clipboard.append((["wl-paste", "--no-newline"], "普通剪贴板（回退）"))
    if os.environ.get("DISPLAY"):
        if available("xclip"):
            clipboard.append((["xclip", "-o", "-selection", "clipboard"], "普通剪贴板（回退）"))
        elif available("xsel"):
            clipboard.append((["xsel", "--clipboard", "--output"], "普通剪贴板（回退）"))
    if available("copyq"):
        clipboard.append((["copyq", "clipboard"], "CopyQ 剪贴板（回退）"))
    for command, source in clipboard:
        selected = _command_selection(command, source)
        if selected:
            return selected
    return None

