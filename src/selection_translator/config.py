from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Config:
    provider: str = "deepseek"
    endpoint: str = "https://api.deepseek.com"
    api_key: str = ""
    model: str = "deepseek-v4-flash"
    timeout_seconds: float = 12.0
    copy_translation: bool = True
    max_chars: int = 5000


def config_path() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "selection-translator" / "config.json"


def load_config(path: Path | None = None) -> Config:
    target = path or config_path()
    data: dict[str, Any] = {}
    if target.exists():
        parsed = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError(f"配置必须是 JSON 对象：{target}")
        data = parsed
    allowed = set(Config.__dataclass_fields__)
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"未知配置项：{', '.join(sorted(unknown))}")
    cfg = Config(**data)
    if cfg.provider not in {"deepseek", "libretranslate", "translate-shell"}:
        raise ValueError(f"不支持的 provider：{cfg.provider}")
    if cfg.provider == "deepseek" and not cfg.model.strip():
        raise ValueError("DeepSeek model 不能为空")
    if cfg.timeout_seconds <= 0 or cfg.max_chars <= 0:
        raise ValueError("timeout_seconds 和 max_chars 必须大于 0")
    return cfg
