import pytest
import requests
from requests_mock import Mocker

from toolforge_weld.api_client import ConnectionError, ToolforgeClient
from toolforge_weld.kubernetes_config import fake_kube_config


@pytest.fixture
def fake_api_client() -> ToolforgeClient:
    return ToolforgeClient(
        server="https://example.org/",
        kubeconfig=fake_kube_config(),
        user_agent="fake",
        timeout=5,
    )


def test_ToolforgeClient_make_kwargs(fake_api_client: ToolforgeClient):
    assert fake_api_client.make_kwargs(url="foo/bar/baz") == {
        "url": "https://example.org/foo/bar/baz",
        "timeout": 5,
    }


def test_ToolforgeClient_make_kwargs_url_starts_with_slash(
    fake_api_client: ToolforgeClient,
):
    assert fake_api_client.make_kwargs(url="/bar") == {
        "url": "https://example.org/bar",
        "timeout": 5,
    }


def test_ToolforgeClient_make_kwargs_custom_timeout(fake_api_client: ToolforgeClient):
    assert fake_api_client.make_kwargs(url="foo/bar/baz", timeout=4) == {
        "url": "https://example.org/foo/bar/baz",
        "timeout": 4,
    }


def test_ToolforgeClient_exception_handler(
    fake_api_client: ToolforgeClient, requests_mock: Mocker
):
    requests_mock.get("/400", text="error text", status_code=400)
    requests_mock.get("/404", text="error text", status_code=404)
    requests_mock.get("/502", text="error text", status_code=502)

    class CustomException(Exception):
        def __init__(self, message="", context=None):
            super().__init__(message)
            self.message = message
            self.context = context

    def exception_handler(original: requests.exceptions.HTTPError) -> Exception:
        if original.response.status_code == 400:
            return CustomException(
                message=f"Custom 400 error with {original.response.text}", context={}
            )
        return CustomException(message="Custom another error", context={})

    def connect_exception_handler(error: ConnectionError) -> Exception:
        raise CustomException(message="Connection error", context={})

    fake_api_client.exception_handler = exception_handler
    fake_api_client.connect_exception_handler = connect_exception_handler

    with pytest.raises(CustomException) as excinfo:
        assert fake_api_client.get("/400") is None
    assert excinfo.value.message == "Custom 400 error with error text"
    assert excinfo.value.context == {}

    with pytest.raises(CustomException) as excinfo:
        assert fake_api_client.get("/404") is None
    assert excinfo.value.message == "Custom another error"
    assert excinfo.value.context == {}

    with pytest.raises(CustomException) as excinfo:
        assert fake_api_client.get("/502") is None
    assert excinfo.value.message == "Connection error"
    assert excinfo.value.context == {}


def test_ToolforgeClient_display_messages(capfd, fake_api_client: ToolforgeClient):
    response = {
        "messages": {
            "error": ["error message"],
            "warning": ["warning message"],
            "info": ["info message"],
        }
    }
    fake_api_client._display_messages(response)
    out, err = capfd.readouterr()
    assert response["messages"]["info"][0] in out
    assert response["messages"]["warning"][0] in err
    assert response["messages"]["error"][0] not in out
    assert response["messages"]["error"][0] not in err
