import unittest
from unittest.mock import patch

from selection_translator.cli import main


class CliTests(unittest.TestCase):
    @patch("selection_translator.cli._run", return_value=0)
    def test_plain_text_is_translation_input(self, run_mock):
        self.assertEqual(main(["Hello"]), 0)
        run_mock.assert_called_once_with("Hello", False)

    @patch("selection_translator.cli._doctor", return_value=0)
    def test_doctor_command(self, doctor_mock):
        self.assertEqual(main(["doctor"]), 0)
        doctor_mock.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
