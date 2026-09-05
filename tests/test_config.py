import json
import tempfile
import unittest
from pathlib import Path

from selection_translator.config import load_config


class ConfigTests(unittest.TestCase):
    def test_defaults_when_missing(self):
        config = load_config(Path("/definitely/missing/config.json"))
        self.assertEqual(config.provider, "deepseek")
        self.assertEqual(config.model, "deepseek-v4-flash")

    def test_load_and_reject_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps({"provider": "translate-shell"}), encoding="utf-8")
            self.assertEqual(load_config(path).provider, "translate-shell")
            path.write_text(json.dumps({"mystery": True}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
