import unittest
from pydantic import TypeAdapter
from app.core.game.typing import URIApp, URIAppHttps, URIHttp


class TestGameTyping(unittest.TestCase):
    """Tests for game typing declarations."""

    def test_uri_app_https_accepts_https_and_app_uris(self) -> None:
        """The combined URI type accepts supported protocols."""
        adapter = TypeAdapter(URIAppHttps)

        assert (
            adapter.validate_python("https://example.com")
            == "https://example.com")
        assert adapter.validate_python("app://example") == "app://example"

    def test_uri_http_accepts_https_uris(self) -> None:
        """The HTTP URI type accepts HTTPS URIs."""
        uri = "https://example.com"
        assert TypeAdapter(URIHttp).validate_python(uri) == uri

    def test_uri_http_rejects_app_uris(self) -> None:
        """The HTTP URI type rejects app URIs."""
        with self.assertRaises(ValueError) as error:
            assert TypeAdapter(URIHttp).validate_python("app://example")
        assert "Value error, URI just supports https protocol" in str(
            error.exception)

    def test_uri_app_accepts_app_uris(self) -> None:
        """The app URI type accepts app URIs."""
        uri = "app://example"
        assert TypeAdapter(URIApp).validate_python(uri) == uri

    def test_uri_app_rejects_https_uris(self) -> None:
        """The app URI type rejects HTTPS URIs."""
        with self.assertRaises(ValueError) as error:
            assert TypeAdapter(URIApp).validate_python("https://example.com")
        assert "Value error, URI just supports app protocol" in str(
            error.exception)
