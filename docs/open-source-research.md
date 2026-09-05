# 开源方案与官方资料调研（2026-09-05）

## 成熟项目

### Crow Translate

- 项目：https://github.com/crow-translate/crow-translate
- 许可证：GPL-3.0
- 可借鉴设计：翻译选区、CLI/DBus 动作、多 provider；Wayland 下明确建议把 DBus 命令绑定到桌面环境快捷键，而不是应用自行抓全局按键。
- 对本 MVP 的影响：使用 GNOME 自定义快捷键启动一次性命令。未复制其 GPL 代码。

### Pot Desktop

- 项目：https://github.com/pot-app/pot-desktop
- 许可证：GPL-3.0
- 可借鉴设计：划词、外部调用、插件式翻译服务；文档明确说明 Wayland 下鼠标坐标/窗口定位受限。
- 对本 MVP 的影响：不尝试在鼠标附近开浮窗，只发桌面通知；provider 单独分层。未复制其 GPL 代码。

### Translate Shell

- 项目：https://github.com/soimort/translate-shell
- 许可证：Public Domain（仓库 LICENSE/WAIVER）
- 可借鉴设计：将翻译引擎放在 CLI 后端，保持桌面集成与 provider 解耦。
- 对本 MVP 的影响：提供可选 `translate-shell` provider，作为外部进程调用，不内嵌其实现。

### CopyQ

- 项目：https://github.com/hluk/CopyQ
- 文档：https://copyq.readthedocs.io/en/stable/scripting-api.html
- 许可证：GPL-3.0
- 可借鉴设计：区分 PRIMARY 与普通 clipboard，并通过桌面设置解决部分 Wayland 全局快捷键限制。其文档指出 Wayland PRIMARY 依赖 compositor/KGuiAddons，GNOME 需要额外扩展方案。
- 对本 MVP 的影响：保留 CopyQ 为普通剪贴板兜底，但不要求用户安装/运行它，也不复制其代码。

### wl-clipboard

- 项目：https://github.com/bugaevc/wl-clipboard
- 许可证：GPL-3.0
- 可借鉴设计：`wl-paste --primary` 与 `wl-copy` 是 Wayland 命令行剪贴板接口。
- 对本 MVP 的影响：作为独立系统工具调用，不复制其实现。

## 官方/协议资料

- Wayland primary-selection-unstable-v1：https://wayland.app/protocols/primary-selection-unstable-v1
  - PRIMARY 是独立于普通剪贴板的选择通道；offer 的可见性和读取受键盘焦点、serial 与 compositor 策略约束。
- GNOME 自定义快捷键：https://help.gnome.org/gnome-help/keyboard-shortcuts-set.html
  - GNOME 设置支持把任意有效命令绑定为自定义快捷键。
- AT-SPI Text：https://docs.gtk.org/atspi2/iface.Text.html
  - `Text` 接口提供 `get_n_selections`、`get_selection` 和 `get_text`；前提是目标应用正确暴露无障碍文本模型。
- Desktop Notifications Specification：https://specifications.freedesktop.org/notification-spec/latest/
  - `notify-send` 通过标准桌面通知服务展示摘要和正文。
- LibreTranslate API：https://docs.libretranslate.com/guides/api_usage/
  - 标准 `/translate` 请求包含 `q`、`source`、`target`、`format`，托管实例可要求 `api_key`。

## 取舍结论

1. Wayland 没有一个允许任意后台 CLI 无条件抓取所有应用选区的通用安全接口，因此不承诺 100% 应用覆盖。
2. 快捷键由 GNOME 管理，避免 root、`xdotool` 和全局键盘监听。
3. 选区按 Wayland PRIMARY、X11 PRIMARY、AT-SPI、普通剪贴板分层，并向用户标识命中来源。
4. 通知取代跟随鼠标的窗口，避免 Wayland 坐标与焦点问题。
5. 翻译 provider 与桌面逻辑解耦，在线发送行为必须显式记录；敏感文本应使用可信自托管服务。

