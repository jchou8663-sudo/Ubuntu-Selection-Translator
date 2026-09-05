# Ubuntu Selection Translator

Ubuntu Selection Translator 是一个面向 Ubuntu GNOME 的全局划词翻译工具。

在任意应用中选中文字，按下你设置的全局快捷键，译文会以半透明浮层显示在鼠标旁边。程序会自动判断英译汉或汉译英，并将译文复制到剪贴板，不会打开常规窗口。

## 功能

- 英文与中文自动互译
- 支持 Ubuntu GNOME Wayland 和 X11
- 在划词位置旁显示简洁的半透明译文
- 自动复制译文
- 支持 DeepSeek、LibreTranslate 和 Translate Shell
- 不常驻后台，不监听键盘

## 获取代码

clone GitHub 仓库，获取项目代码：

```bash
git clone https://github.com/jchou8663-sudo/Ubuntu-Selection-Translator.git
cd ubuntu-selection-translator
```

也可以在 GitHub 仓库页面点击 **Code → Download ZIP**，解压后进入项目目录。

## 安装

先安装 Ubuntu 依赖：

```bash
sudo apt update
sudo apt install python3 python3-venv python3-setuptools libnotify-bin wl-clipboard xclip python3-pyatspi
```

然后运行安装脚本：

```bash
./scripts/install.sh
~/.local/bin/selection-translator doctor
```

程序会安装到独立的用户级 Python 环境，不会修改系统 Python。重复运行安装脚本即可升级，已有配置不会被覆盖。

安装脚本还会安装 GNOME 46 浮层扩展。首次安装后，如果提示扩展暂时无法启用，请注销并重新登录一次，然后运行：

```bash
gnome-extensions enable selection-translator@jchou8663-sudo.github.com
```

## 配置翻译服务

配置文件位于：

```text
~/.config/selection-translator/config.json
```

默认使用 DeepSeek。编辑配置文件并填入你的 API Key：

```json
{
  "provider": "deepseek",
  "endpoint": "https://api.deepseek.com",
  "api_key": "你的-deepseek-api-key",
  "model": "deepseek-v4-flash",
  "timeout_seconds": 12,
  "copy_translation": true,
  "max_chars": 5000
}
```

保护配置文件权限：

```bash
chmod 600 ~/.config/selection-translator/config.json
```

也可以不把 Key 写入文件，而是在运行程序的环境中设置：

```bash
export DEEPSEEK_API_KEY="你的-deepseek-api-key"
```

但 GNOME 快捷键通常不会读取终端的临时环境变量，因此桌面快捷键场景建议使用权限为 `600` 的配置文件。

`deepseek-v4-flash` 速度和费用更适合划词翻译；如需更高质量，可将 `model` 改成 `deepseek-v4-pro`。

如需使用 LibreTranslate，可改为：

```json
{
  "provider": "libretranslate",
  "endpoint": "你的 LibreTranslate 服务地址",
  "api_key": "",
  "model": "deepseek-v4-flash",
  "timeout_seconds": 12,
  "copy_translation": true,
  "max_chars": 5000
}
```

也可以安装 [Translate Shell](https://github.com/soimort/translate-shell)，然后将 `provider` 改为：

```json
"provider": "translate-shell"
```

测试翻译服务：

```bash
~/.local/bin/selection-translator "Hello"
~/.local/bin/selection-translator "你好"
```

文字会发送到你配置的翻译服务，请不要提交密码、Token 等敏感内容。

## 设置全局快捷键

本工具不需要设置开机启动，也没有常驻后台进程。登录桌面后，GNOME 会保存并自动启用自定义快捷键；只有按下快捷键时程序才会启动，翻译完成后立即退出。空闲时不会占用 DeepSeek API 额度。

打开 Ubuntu：

**设置 → 键盘 → 查看及自定义快捷键 → 自定义快捷键 → 添加**

填写：

- 名称：`划词翻译`
- 命令：`/home/你的用户名/.local/bin/selection-translator`
- 快捷键：`Alt+Q`

先在终端运行一次完整命令，确认路径正确。

`Alt+Q` 可能已经被个别应用使用。设置成 GNOME 全局快捷键后，系统通常会优先处理它，该应用原有的 `Alt+Q` 功能可能无法继续使用。

## 使用

1. 在浏览器、编辑器或其他应用中选中文字。
2. 按下 `Alt+Q`。
3. 在鼠标旁的半透明浮层中查看译文；浮层约 4 秒后自动淡出。
4. 译文已经复制到剪贴板，可以直接粘贴。

如果某些 Wayland 应用无法直接读取选区，请使用：

```text
选中文字 → Ctrl+C → Alt+Q
```

常用命令：

```bash
# 翻译当前选区
selection-translator

# 翻译指定文字
selection-translator "Hello"

# 本次不复制译文
selection-translator --no-copy "Hello"

# 检查配置和依赖
selection-translator doctor

# 显示配置文件位置
selection-translator config-path
```

## 修改和开发

源码位于：

```text
src/selection_translator/
```

主要文件：

- `cli.py`：命令行入口和执行流程
- `selection.py`：读取选区
- `providers.py`：翻译服务
- `desktop.py`：通知和剪贴板
- `config.py`：配置读取

修改代码后运行测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
bash -n scripts/install.sh scripts/uninstall.sh
```

重新安装修改后的版本：

```bash
./scripts/install.sh
```

如需增加新的翻译服务，在 `providers.py` 中添加实现，并在 `config.py` 中允许新的 provider 名称。

## 卸载

```bash
./scripts/uninstall.sh
```

卸载脚本会删除程序的虚拟环境和启动入口，但会保留配置文件。GNOME 全局快捷键需要在系统设置中手动删除。
同时会禁用并删除本工具安装的 GNOME 翻译浮层扩展。

## 许可证

[MIT](LICENSE)
