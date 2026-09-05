import unittest
from unittest.mock import patch

from selection_translator.desktop import show_translation
from selection_translator.process import CommandResult


class DesktopTests(unittest.TestCase):
    @patch("selection_translator.desktop.available", return_value=True)
    @patch("selection_translator.desktop.run", return_value=CommandResult(True))
    def test_show_translation_uses_gnome_extension_dbus(self, run_mock, available_mock):
        del available_mock
        self.assertTrue(show_translation("你好"))
        command = run_mock.call_args.args[0]
        self.assertEqual(command[0:3], ["gdbus", "call", "--session"])
        self.assertIn("io.github.jchou8663.SelectionTranslator.Show", command)
        self.assertEqual(command[-1], "你好")

    @patch("selection_translator.desktop.available", return_value=False)
    def test_show_translation_without_gdbus(self, available_mock):
        del available_mock
        self.assertFalse(show_translation("你好"))


if __name__ == "__main__":
    unittest.main()
