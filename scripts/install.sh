#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
data_root="${XDG_DATA_HOME:-$HOME/.local/share}"
config_root="${XDG_CONFIG_HOME:-$HOME/.config}"
bin_dir="${XDG_BIN_HOME:-$HOME/.local/bin}"
app_dir="$data_root/selection-translator"
venv_dir="$app_dir/venv"
marker="$venv_dir/.selection-translator-managed"
entry="$bin_dir/selection-translator"
entry_marker="# selection-translator managed launcher"
translator_python="${SELECTION_TRANSLATOR_PYTHON:-python3}"

if ! command -v "$translator_python" >/dev/null 2>&1; then
  echo "错误：找不到 Python：$translator_python" >&2
  echo "请安装 python3 和 python3-venv 后重试。" >&2
  exit 1
fi

if [[ -e "$venv_dir" && ! -f "$marker" ]]; then
  echo "错误：$venv_dir 已存在，但不是本安装脚本创建的环境；为保护数据不会覆盖。" >&2
  exit 1
fi

if [[ ! -x "$venv_dir/bin/python" ]]; then
  mkdir -p "$app_dir"
  temp_venv="$app_dir/venv.new.$$"
  cleanup() { rm -rf -- "$temp_venv"; }
  trap cleanup EXIT
  if ! "$translator_python" -m venv --system-site-packages "$temp_venv"; then
    echo >&2
    echo "无法创建 Python 虚拟环境。Ubuntu/Debian 请先运行：" >&2
    echo "  sudo apt install python3-venv python3-setuptools" >&2
    exit 1
  fi
  : > "$temp_venv/.selection-translator-managed"
  mv -- "$temp_venv" "$venv_dir"
  trap - EXIT
fi

if ! "$venv_dir/bin/python" -m pip --version >/dev/null 2>&1; then
  echo "错误：虚拟环境中没有 pip。请安装 python3-venv 后删除 $venv_dir 并重试。" >&2
  exit 1
fi

"$venv_dir/bin/python" -m pip install \
  --disable-pip-version-check \
  --no-deps \
  --no-build-isolation \
  --force-reinstall \
  "$project_dir"

mkdir -p "$bin_dir"
if [[ -e "$entry" || -L "$entry" ]]; then
  if [[ ! -f "$entry" || "$(head -n 2 -- "$entry" | tail -n 1)" != "$entry_marker" ]]; then
    echo "错误：入口 $entry 已存在且不属于本应用；不会覆盖。" >&2
    exit 1
  fi
fi
temp_entry="$bin_dir/.selection-translator.new.$$"
cleanup_entry() { rm -f -- "$temp_entry"; }
trap cleanup_entry EXIT
printf '#!/usr/bin/env bash\n%s\nexec %q -m selection_translator.cli "$@"\n' \
  "$entry_marker" "$venv_dir/bin/python" > "$temp_entry"
chmod 755 "$temp_entry"
mv -f -- "$temp_entry" "$entry"
trap - EXIT

config_dir="$config_root/selection-translator"
mkdir -p "$config_dir"
if [[ ! -e "$config_dir/config.json" ]]; then
  cp -- "$project_dir/config.example.json" "$config_dir/config.json"
  echo "已创建配置：$config_dir/config.json"
else
  echo "保留已有配置：$config_dir/config.json"
fi

echo "安装/升级完成。先运行：$entry doctor"
echo "GNOME 自定义快捷键命令：$entry"
