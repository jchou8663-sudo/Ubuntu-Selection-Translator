from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__
from .config import config_path, load_config
from .desktop import notify, show_translation
from .language import translation_direction
from .process import available
from .providers import TranslationError, translate
from .selection import get_selection


def _doctor() -> int:
    cfg_path = config_path()
    checks = {
        "version": __version__,
        "session_type": os.environ.get("XDG_SESSION_TYPE", "unknown"),
        "wayland_display": bool(os.environ.get("WAYLAND_DISPLAY")),
        "x11_display": bool(os.environ.get("DISPLAY")),
        "config_path": str(cfg_path),
        "config_exists": cfg_path.exists(),
        "commands": {name: available(name) for name in ("wl-paste", "wl-copy", "xclip", "xsel", "copyq", "notify-send", "trans")},
    }
    try:
        cfg = load_config()
        checks["provider"] = cfg.provider
        checks["provider_endpoint"] = cfg.endpoint if cfg.provider == "libretranslate" else "local command: trans"
        if cfg.provider == "deepseek":
            checks["provider_endpoint"] = cfg.endpoint
            checks["provider_model"] = cfg.model
            checks["api_key_configured"] = bool(os.environ.get("DEEPSEEK_API_KEY") or cfg.api_key)
        checks["config_valid"] = True
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        checks["config_valid"] = False
        checks["config_error"] = str(exc)
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    commands = checks["commands"]
    has_reader = any(commands[name] for name in ("wl-paste", "xclip", "xsel", "copyq"))
    return 0 if checks.get("config_valid") and has_reader and commands["notify-send"] else 1


def _run(text_arg: str | None) -> int:
    try:
        cfg = load_config()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        notify("划词翻译：配置错误", str(exc), urgency="critical")
        return 2
    selected = None if text_arg is not None else get_selection()
    text = text_arg.strip() if text_arg is not None else (selected.text if selected else "")
    if not text:
        message = "未读到选区；请复制文字后重试，或运行 doctor 检查依赖。"
        print(message, file=sys.stderr)
        notify("划词翻译", message, urgency="critical")
        return 3
    if len(text) > cfg.max_chars:
        message = f"文本过长（{len(text)} > {cfg.max_chars}），已取消上传。"
        print(message, file=sys.stderr)
        notify("划词翻译", message, urgency="critical")
        return 4
    source, target = translation_direction(text)
    try:
        result = translate(text, source, target, cfg)
    except TranslationError as exc:
        print(str(exc), file=sys.stderr)
        notify("划词翻译失败", str(exc), urgency="critical")
        return 5
    if not show_translation(result.text):
        notify("Translator Result", result.text)
    print(result.text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ubuntu 全局划词翻译")
    parser.add_argument("text", nargs="?", help="直接翻译文本；doctor/config-path 为诊断命令；省略时读取选区")
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.text == "doctor":
        return _doctor()
    if args.text == "config-path":
        print(config_path())
        return 0
    return _run(args.text)


if __name__ == "__main__":
    raise SystemExit(main())
