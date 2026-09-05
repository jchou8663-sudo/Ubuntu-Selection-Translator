import io
import unittest
from unittest.mock import patch

from selection_translator.config import Config
from selection_translator.providers import translate


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class ProviderTests(unittest.TestCase):
    @patch("urllib.request.urlopen", return_value=FakeResponse(b'{"translatedText":"hello"}'))
    def test_libretranslate_response(self, urlopen):
        result = translate("你好", "zh", "en", Config())
        self.assertEqual(result.text, "hello")
        request = urlopen.call_args.args[0]
        self.assertIn(b"source=zh", request.data)
        self.assertIn(b"target=en", request.data)


if __name__ == "__main__":
    unittest.main()

