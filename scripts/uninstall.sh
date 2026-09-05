#!/usr/bin/env bash
set -euo pipefail

data_root="${XDG_DATA_HOME:-$HOME/.local/share}"
config_root="${XDG_CONFIG_HOME:-$HOME/.config}"
bin_dir="${XDG_BIN_HOME:-$HOME/.local/bin}"
app_dir="$data_root/selection-translator"
venv_dir="$app_dir/venv"
marker="$venv_dir/.selection-translator-managed"
entry="$bin_dir/selection-translator"
entry_marker="# selection-translator managed launcher"

if [[ -f "$entry" && "$(head -n 2 -- "$entry" | tail -n 1)" == "$entry_marker" ]]; then
  rm -- "$entry"
  echo "已删除入口：$entry"
elif [[ -e "$entry" || -L "$entry" ]]; then
  echo "保留非本应用管理的入口：$entry"
fi

if [[ -f "$marker" ]]; then
  rm -rf -- "$venv_dir"
  rmdir --ignore-fail-on-non-empty "$app_dir" 2>/dev/null || true
  echo "已删除应用虚拟环境：$venv_dir"
elif [[ -e "$venv_dir" ]]; then
  echo "保留没有管理标记的目录：$venv_dir"
fi

echo "卸载完成。配置仍保留在：$config_root/selection-translator"
