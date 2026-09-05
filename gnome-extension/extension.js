import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import Pango from 'gi://Pango';
import Shell from 'gi://Shell';
import St from 'gi://St';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const BUS_NAME = 'io.github.jchou8663.SelectionTranslator';
const OBJECT_PATH = '/io/github/jchou8663/SelectionTranslator';
const INTERFACE_XML = `
<node>
  <interface name="io.github.jchou8663.SelectionTranslator">
    <method name="Show">
      <arg type="s" name="text" direction="in"/>
    </method>
  </interface>
</node>`;

export default class SelectionTranslatorExtension extends Extension {
    enable() {
        this._backdrop = null;
        this._dialog = null;
        this._dbus = Gio.DBusExportedObject.wrapJSObject(INTERFACE_XML, this);
        this._dbus.export(Gio.DBus.session, OBJECT_PATH);
        this._nameId = Gio.bus_own_name_on_connection(
            Gio.DBus.session,
            BUS_NAME,
            Gio.BusNameOwnerFlags.NONE,
            null,
            null
        );
    }

    disable() {
        this._removeDialog();
        if (this._nameId) {
            Gio.bus_unown_name(this._nameId);
            this._nameId = 0;
        }
        if (this._dbus) {
            this._dbus.unexport();
            this._dbus = null;
        }
    }

    Show(text) {
        const translation = text.trim();
        if (!translation)
            return;

        this._removeDialog();
        this._backdrop = new St.Widget({
            style_class: 'selection-translator-backdrop',
            reactive: true,
            x: 0,
            y: 0,
            width: global.stage.width,
            height: global.stage.height,
        });
        this._backdrop.connect('button-press-event', () => {
            this._removeDialog();
            return Clutter.EVENT_STOP;
        });
        Main.layoutManager.addTopChrome(this._backdrop, {
            affectsInputRegion: true,
            trackFullscreen: true,
        });

        this._dialog = new St.BoxLayout({
            style_class: 'selection-translator-dialog',
            vertical: true,
            reactive: true,
            can_focus: true,
        });
        this._dialog.add_effect_with_name('background-blur', new Shell.BlurEffect({
            brightness: 0.92,
            radius: 28,
            mode: Shell.BlurMode.BACKGROUND,
        }));

        const header = new St.BoxLayout({
            style_class: 'selection-translator-header',
            vertical: false,
        });
        const icon = new St.Icon({
            style_class: 'selection-translator-icon',
            icon_name: 'accessories-dictionary-symbolic',
        });
        const title = new St.Label({
            style_class: 'selection-translator-title',
            text: '即时翻译',
        });
        header.add_child(icon);
        header.add_child(title);

        const scrollView = new St.ScrollView({
            style_class: 'selection-translator-scroll',
            overlay_scrollbars: true,
            x_expand: true,
            y_expand: true,
        });
        scrollView.set_policy(St.PolicyType.NEVER, St.PolicyType.AUTOMATIC);
        const result = new St.Label({
            style_class: 'selection-translator-result',
            text: translation,
            reactive: true,
            can_focus: true,
            x_expand: true,
            x_align: Clutter.ActorAlign.FILL,
        });
        const resultText = result.clutter_text;
        resultText.line_wrap = true;
        resultText.line_wrap_mode = Pango.WrapMode.WORD_CHAR;
        resultText.ellipsize = Pango.EllipsizeMode.NONE;
        resultText.selectable = true;
        resultText.editable = false;
        result.connect('button-press-event', () => {
            global.stage.set_key_focus(resultText);
            return Clutter.EVENT_PROPAGATE;
        });
        resultText.connect('key-press-event', (_actor, event) => {
            const symbol = event.get_key_symbol();
            if (symbol === Clutter.KEY_Escape) {
                this._removeDialog();
                return Clutter.EVENT_STOP;
            }
            if ((event.get_state() & Clutter.ModifierType.CONTROL_MASK) &&
                (symbol === Clutter.KEY_c || symbol === Clutter.KEY_C)) {
                const selected = resultText.get_selection();
                if (selected)
                    St.Clipboard.get_default().set_text(St.ClipboardType.CLIPBOARD, selected);
                return Clutter.EVENT_STOP;
            }
            return Clutter.EVENT_PROPAGATE;
        });
        scrollView.add_child(result);
        this._dialog.add_child(header);
        this._dialog.add_child(scrollView);
        Main.layoutManager.addTopChrome(this._dialog, {
            affectsInputRegion: true,
            trackFullscreen: true,
        });

        const monitor = Main.layoutManager.currentMonitor;
        const workArea = Main.layoutManager.getWorkAreaForMonitor(monitor.index);
        const maxWidth = Math.min(900, workArea.width - 64);
        const [, naturalWidth] = this._dialog.get_preferred_width(-1);
        const width = Math.min(Math.max(420, naturalWidth), maxWidth);
        this._dialog.set_width(width);
        const [, naturalHeight] = this._dialog.get_preferred_height(width);
        const height = Math.min(naturalHeight, Math.round(workArea.height * 0.72));
        this._dialog.set_height(height);
        this._dialog.set_position(
            Math.round(workArea.x + (workArea.width - width) / 2),
            workArea.y + 24
        );
        global.stage.set_key_focus(resultText);
    }

    _removeDialog() {
        if (this._dialog) {
            this._dialog.destroy();
            this._dialog = null;
        }
        if (this._backdrop) {
            this._backdrop.destroy();
            this._backdrop = null;
        }
    }
}
