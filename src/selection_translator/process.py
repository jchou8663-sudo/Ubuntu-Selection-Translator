from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    stdout: str = ""
    stderr: str = ""


def available(command: str) -> bool:
    return shutil.which(command) is not None


def run(command: list[str], *, input_text: str | None = None, timeout: float = 2.0) -> CommandResult:
    try:
        result = subprocess.run(
            command,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return CommandResult(result.returncode == 0, result.stdout, result.stderr)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CommandResult(False, stderr=str(exc))

