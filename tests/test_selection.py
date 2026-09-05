import os
import sys
import types
import unittest
from unittest.mock import patch

from selection_translator.process import CommandResult
from selection_translator.selection import Selection, _atspi_selection, get_selection


class SelectionTests(unittest.TestCase):
    def test_atspi_ignores_stale_none_nodes(self):
        class Root:
            def getState(self):
                return types.SimpleNamespace(contains=lambda _state: False)

            def __iter__(self):
                return iter([None])

        fake_pyatspi = types.SimpleNamespace(
            STATE_FOCUSED=1,
            Registry=types.SimpleNamespace(getDesktop=lambda _index: Root()),
        )
        with patch.dict(sys.modules, {"pyatspi": fake_pyatspi}):
            self.assertIsNone(_atspi_selection())

    @patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland", "WAYLAND_DISPLAY": "wayland-0"}, clear=True)
    @patch("selection_translator.selection._atspi_selection", return_value=None)
    @patch("selection_translator.selection.available", side_effect=lambda name: name in {"wl-paste", "copyq"})
    @patch("selection_translator.selection.run")
    def test_primary_precedes_clipboard(self, run_mock, available_mock, atspi_mock):
        del available_mock, atspi_mock
        run_mock.return_value = CommandResult(True, "selected text")
        result = get_selection()
        self.assertEqual(result.source, "Wayland PRIMARY")
        run_mock.assert_called_once_with(["wl-paste", "--primary", "--no-newline"])

    @patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland"}, clear=True)
    @patch("selection_translator.selection._atspi_selection", return_value=None)
    @patch("selection_translator.selection.available", side_effect=lambda name: name == "wl-paste")
    @patch("selection_translator.selection.run")
    def test_empty_primary_falls_back_to_clipboard(self, run_mock, available_mock, atspi_mock):
        del available_mock, atspi_mock
        run_mock.side_effect = [CommandResult(True, ""), CommandResult(True, "copied text")]
        result = get_selection()
        self.assertEqual(result.source, "普通剪贴板（回退）")
        self.assertEqual(result.text, "copied text")

if __name__ == "__main__":
    unittest.main()
