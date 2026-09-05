# Ubuntu 全局划词翻译 MVP

在任意应用选中文字后按 GNOME 全局快捷键，程序会自动判断英译汉或汉译英，通过桌面通知显示结果，并把译文写入普通剪贴板。它是一次性 CLI，不打开常规主窗口、不驻留、不监听键盘，也不需要 root。

## 工作方式与边界

读取顺序如下，命中后停止：

1. Wayland 会话：`wl-paste --primary`；
2. 有 X11/XWayland display：`xclip` 或 `xsel` 的 PRIMARY；
3. 可选 AT-SPI：聚焦控件公开的文本选区（需 `python3-pyatspi`）；
4. 普通剪贴板回退（`wl-paste`、`xclip`/`xsel`、CopyQ）。

GNOME Wayland 遵循隔离模型，后台 CLI 对 PRIMARY 的读取能力取决于 Mutter、工具版本和源应用；部分原生 Wayland 应用不会公开 PRIMARY，部分 Electron/浏览器控件也不会公开 AT-SPI 选区。因此普通剪贴板回退是必要的：遇到取不到的应用，请先 `Ctrl+C` 再按翻译快捷键。通知会标明实际文本来源，避免把旧剪贴板内容误认为当前选区。

译文默认写入普通剪贴板，这是用户触发后的明确行为，通知会显示“已复制译文”。如不希望覆盖剪贴板，使用 `--no-copy` 或把配置中的 `copy_translation` 改为 `false`。程序不会改写 PRIMARY。

## 安装

Ubuntu 推荐依赖：

```bash
sudo apt install python3 python3-venv python3-setuptools libnotify-bin wl-clipboard xclip python3-pyatspi
./scripts/install.sh
~/.local/bin/selection-translator doctor
```

依赖可以按会话精简：Wayland 需要 `wl-clipboard`，X11 需要 `xclip`（也支持 `xsel`），通知需要 `libnotify-bin`。AT-SPI 是尽力而为的可选增强。

安装脚本不会调用 `pip --user` 或 `--break-system-packages`，因此兼容 Ubuntu Python 3.12 的 PEP 668。它会创建启用系统包访问的独立环境（从而能使用 apt 安装的 `python3-pyatspi`）：

```bash
${XDG_DATA_HOME:-$HOME/.local/share}/selection-translator/venv
```

稳定入口位于 `${XDG_BIN_HOME:-$HOME/.local/bin}/selection-translator`。如果无法创建 venv，安装脚本会停止并提示安装 `python3-venv`；不会留下半成品环境。重复执行安装脚本就是升级，已有配置会原样保留：

```bash
git pull                    # 若项目通过 Git 获取
./scripts/install.sh        # 重新构建并安装当前源码
~/.local/bin/selection-translator --version
```

## 配置翻译服务

首次安装会把 `config.example.json` 复制到：

```text
~/.config/selection-translator/config.json
```

默认 provider 是 LibreTranslate，调用标准 `POST /translate` API。公共实例可能要求 API key、限流或改变政策；推荐使用自己的 LibreTranslate 实例，并填写 `endpoint` 和 `api_key`。可先直接验证：

```bash
selection-translator "Hello from Ubuntu"
selection-translator "你好，Ubuntu"
```

也可安装 Translate Shell 后使用其 provider：

```json
{
  "provider": "translate-shell",
  "endpoint": "",
  "api_key": "",
  "timeout_seconds": 12,
  "copy_translation": true,
  "max_chars": 5000
}
```

Translate Shell 自身可能调用 Google/Bing 等在线服务，其具体隐私与可用性由它选择的后端决定。本项目的 provider 接口集中在 `src/selection_translator/providers.py`，后续接 OpenAI 或 DeepL 时只需增加实现与配置分支。

### 隐私说明

触发翻译后，所选文字会发送到所配置的在线翻译端点。不要翻译密码、令牌、客户资料或其他敏感内容，除非使用可信的自托管服务。程序不会后台监听或保存选区；但桌面通知服务、剪贴板管理器和 provider 可能各自留有历史。`max_chars` 可限制意外上传量。

## 配置 GNOME 全局快捷键

打开“设置 → 键盘 → 查看及自定义快捷键 → 自定义快捷键 → +”：

- 名称：`划词翻译`
- 命令：`/home/你的用户名/.local/bin/selection-translator`（若设置了 `XDG_BIN_HOME`，使用该目录下的入口）
- 快捷键：例如 `Ctrl+Alt+T`（请选择不冲突的组合）

这是 GNOME 官方支持的应用启动快捷键机制；程序自身不注册或监听全局按键。建议先在终端运行完整命令确认正常，再绑定快捷键。

## 使用与诊断

```bash
# 读取当前选区并翻译
selection-translator

# 显式文本（也用于 provider 冒烟测试）
selection-translator "Hello"

# 本次不改剪贴板
selection-translator --no-copy "Hello"

# 输出会话、配置和工具状态（JSON）
selection-translator doctor

# 定位配置
selection-translator config-path
```

`doctor` 返回非零通常表示缺少选区读取工具、`notify-send` 或配置无效。它不发送测试文本到网络。

## 测试

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall -q src tests
PYTHONPATH=src python3 -m selection_translator.cli --version
PYTHONPATH=src python3 -m selection_translator.cli doctor
```

无图形会话的 CI 只能验证核心逻辑、provider 协议和诊断输出；PRIMARY、AT-SPI、GNOME 快捷键、通知和剪贴板写入必须在真实 Ubuntu GNOME Wayland/X11 登录会话最终验收。

## 卸载

```bash
./scripts/uninstall.sh
```

脚本不会删除用户配置，也不会擅自修改 GNOME 快捷键；请在“设置 → 键盘 → 自定义快捷键”中手动移除对应条目。
卸载只会删除带有本应用管理标记的独立 venv 和启动入口；同路径下不属于本应用的文件会被保留。

## 开源调研与设计来源

详见 [`docs/open-source-research.md`](docs/open-source-research.md)。本项目只借鉴公开设计思路，没有复制上述项目代码；自身以 MIT 许可证发布。
