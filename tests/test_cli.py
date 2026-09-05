import unittest
from types import SimpleNamespace
from unittest.mock import patch

from selection_translator.cli import _run, main


class CliTests(unittest.TestCase):
    @patch("selection_translator.cli._run", return_value=0)
    def test_plain_text_is_translation_input(self, run_mock):
        self.assertEqual(main(["Hello"]), 0)
        run_mock.assert_called_once_with("Hello")

    @patch("selection_translator.cli._doctor", return_value=0)
    def test_doctor_command(self, doctor_mock):
        self.assertEqual(main(["doctor"]), 0)
        doctor_mock.assert_called_once_with()

    @patch("selection_translator.cli.notify")
    @patch("selection_translator.cli.show_translation", return_value=False)
    @patch("selection_translator.cli.translate", return_value=SimpleNamespace(text="你好"))
    @patch(
        "selection_translator.cli.load_config",
        return_value=SimpleNamespace(max_chars=5000),
    )
    def test_notification_fallback_has_plain_title(
        self, _config_mock, _translate_mock, _show_mock, notify_mock
    ):
        self.assertEqual(_run("Hello"), 0)
        notify_mock.assert_called_once_with("Translator Result", "你好")


if __name__ == "__main__":
    unittest.main()
