from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from .config import Config
from .process import available, run


class TranslationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Translation:
    text: str
    provider: str


def _libretranslate(text: str, source: str, target: str, cfg: Config) -> Translation:
    url = cfg.endpoint.rstrip("/") + "/translate"
    fields = {"q": text, "source": source, "target": target, "format": "text"}
    if cfg.api_key:
        fields["api_key"] = cfg.api_key
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(fields).encode(),
        headers={"Accept": "application/json", "User-Agent": "selection-translator/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=cfg.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise TranslationError(f"LibreTranslate 请求失败：{exc}") from exc
    translated = payload.get("translatedText") if isinstance(payload, dict) else None
    if not isinstance(translated, str) or not translated.strip():
        detail = payload.get("error") if isinstance(payload, dict) else payload
        raise TranslationError(f"LibreTranslate 返回无效结果：{detail}")
    return Translation(translated.strip(), "LibreTranslate")


def _translate_shell(text: str, source: str, target: str, cfg: Config) -> Translation:
    del cfg
    if not available("trans"):
        raise TranslationError("未安装 Translate Shell（trans）")
    result = run(["trans", "-brief", f"{source}:{target}", text], timeout=20)
    if not result.ok or not result.stdout.strip():
        raise TranslationError(f"Translate Shell 失败：{result.stderr.strip()}")
    return Translation(result.stdout.strip(), "Translate Shell")


def translate(text: str, source: str, target: str, cfg: Config) -> Translation:
    if cfg.provider == "libretranslate":
        return _libretranslate(text, source, target, cfg)
    if cfg.provider == "translate-shell":
        return _translate_shell(text, source, target, cfg)
    raise TranslationError(f"不支持的 provider：{cfg.provider}")

