import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Pango from 'gi://Pango';
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
        this._label = null;
        this._hideTimeout = 0;
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
        this._removeLabel();
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

        this._removeLabel();
        this._label = new St.Label({
            style_class: 'selection-translator-overlay',
            text: translation,
            opacity: 0,
            reactive: false,
        });
        this._label.clutter_text.line_wrap = true;
        this._label.clutter_text.line_wrap_mode = Pango.WrapMode.WORD_CHAR;
        Main.layoutManager.addTopChrome(this._label, {
            affectsInputRegion: false,
            trackFullscreen: true,
        });

        const [pointerX, pointerY] = global.get_pointer();
        const monitor = Main.layoutManager.currentMonitor;
        const [, naturalWidth] = this._label.get_preferred_width(-1);
        const width = Math.min(naturalWidth, 520);
        this._label.set_width(width);
        const [, naturalHeight] = this._label.get_preferred_height(width);
        const x = Math.max(monitor.x + 8, Math.min(pointerX + 16, monitor.x + monitor.width - width - 8));
        let y = pointerY + 22;
        if (y + naturalHeight > monitor.y + monitor.height - 8)
            y = Math.max(monitor.y + 8, pointerY - naturalHeight - 14);
        this._label.set_position(x, y);
        this._label.ease({opacity: 255, duration: 120, mode: Clutter.AnimationMode.EASE_OUT_QUAD});

        this._hideTimeout = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 4000, () => {
            if (this._label) {
                this._label.ease({
                    opacity: 0,
                    duration: 220,
                    mode: Clutter.AnimationMode.EASE_OUT_QUAD,
                    onComplete: () => this._removeLabel(),
                });
            }
            this._hideTimeout = 0;
            return GLib.SOURCE_REMOVE;
        });
    }

    _removeLabel() {
        if (this._hideTimeout) {
            GLib.source_remove(this._hideTimeout);
            this._hideTimeout = 0;
        }
        if (this._label) {
            this._label.destroy();
            this._label = null;
        }
    }
}
