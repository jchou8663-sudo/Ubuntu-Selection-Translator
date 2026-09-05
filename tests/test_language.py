import unittest

from selection_translator.language import translation_direction


class LanguageTests(unittest.TestCase):
    def test_english_to_chinese(self):
        self.assertEqual(translation_direction("Hello, world!"), ("en", "zh"))

    def test_chinese_to_english(self):
        self.assertEqual(translation_direction("你好，世界！"), ("zh", "en"))

    def test_mixed_prefers_dominant_script(self):
        self.assertEqual(translation_direction("Ubuntu 的详细使用方法说明"), ("zh", "en"))


if __name__ == "__main__":
    unittest.main()
