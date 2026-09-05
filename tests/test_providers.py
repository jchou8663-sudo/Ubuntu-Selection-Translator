import io
import json
import os
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
        result = translate(
            "你好",
            "zh",
            "en",
            Config(provider="libretranslate", endpoint="https://libretranslate.com"),
        )
        self.assertEqual(result.text, "hello")
        request = urlopen.call_args.args[0]
        self.assertIn(b"source=zh", request.data)
        self.assertIn(b"target=en", request.data)

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "secret-from-env"}, clear=False)
    @patch(
        "urllib.request.urlopen",
        return_value=FakeResponse(
            b'{"choices":[{"message":{"role":"assistant","content":"hello"}}]}'
        ),
    )
    def test_deepseek_response_and_request(self, urlopen):
        config = Config(provider="deepseek", api_key="secret-from-config")
        result = translate("你好", "zh", "en", config)
        self.assertEqual(result.text, "hello")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.deepseek.com/chat/completions")
        self.assertEqual(request.headers["Authorization"], "Bearer secret-from-env")
        body = json.loads(request.data)
        self.assertEqual(body["model"], "deepseek-v4-flash")
        self.assertEqual(body["thinking"], {"type": "disabled"})
        self.assertEqual(body["messages"][1]["content"], "你好")

    @patch.dict(os.environ, {}, clear=True)
    def test_deepseek_requires_api_key(self):
        with self.assertRaisesRegex(Exception, "API Key"):
            translate("hello", "en", "zh", Config(provider="deepseek"))


if __name__ == "__main__":
    unittest.main()
