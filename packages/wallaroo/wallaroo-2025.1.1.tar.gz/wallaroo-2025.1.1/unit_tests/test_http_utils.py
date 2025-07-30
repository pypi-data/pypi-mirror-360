from unittest.mock import patch

import httpx
import pytest

from wallaroo.http_utils import (
    _get_base_headers,
    _make_get_request,
    _make_post_request,
    _make_put_request,
)


@pytest.mark.parametrize(
    "auth_token,expected_headers",
    [
        # Test with auth token
        (
            "test-token",
            {
                "authorization": "test-token",
                "user-agent": "WallarooSDK/0.0.0",
            },
        ),
        # Test without auth token
        (
            None,
            {
                "authorization": None,
                "user-agent": "WallarooSDK/0.0.0",
            },
        ),
        # Test with empty string token
        (
            "",
            {
                "authorization": "",
                "user-agent": "WallarooSDK/0.0.0",
            },
        ),
    ],
)
def test_get_base_headers(auth_token, expected_headers):
    """Test the base headers formation with various auth token values."""
    headers = _get_base_headers(auth_token)
    assert headers["authorization"] == expected_headers["authorization"]
    assert "user-agent" in headers
    assert headers["user-agent"] == expected_headers["user-agent"]


@pytest.mark.parametrize(
    "api_endpoint,path,headers,expected_url",
    [
        (
            "http://api-lb:8080",
            "test",
            {"Authorization": "Bearer token"},
            "http://api-lb:8080/test",
        ),
        (
            "http://api-lb:8080/",
            "test/path",
            {"Authorization": "Bearer token"},
            "http://api-lb:8080/test/path",
        ),
        (
            "http://api-lb:8080///",
            "test/path",
            {"Authorization": "Bearer token"},
            "http://api-lb:8080/test/path",
        ),
    ],
)
def test_make_get_request(api_endpoint, path, headers, expected_url):
    """Test GET request formation with various parameters."""
    with patch("httpx.get") as mock_get:
        mock_get.return_value = httpx.Response(200)
        _make_get_request(api_endpoint, path, headers)
        mock_get.assert_called_once_with(expected_url, headers=headers)


@pytest.mark.parametrize(
    "api_endpoint,path,headers,json_data,expected_url",
    [
        (
            "http://api-lb:8080",
            "test",
            {"Authorization": "Bearer token"},
            {"key": "value"},
            "http://api-lb:8080/test",
        ),
        (
            "http://api-lb:8080/",
            "test/path",
            {"Authorization": "Bearer token"},
            {"data": [1, 2, 3]},
            "http://api-lb:8080/test/path",
        ),
        (
            "http://api-lb:8080/",
            "///test/path",
            {"Authorization": "Bearer token"},
            {"data": [1, 2, 3]},
            "http://api-lb:8080/test/path",
        ),
    ],
)
def test_make_post_request(api_endpoint, path, headers, json_data, expected_url):
    """Test POST request formation with various parameters."""
    with patch("httpx.post") as mock_post:
        mock_post.return_value = httpx.Response(200)
        _make_post_request(api_endpoint, path, headers, json_data)
        mock_post.assert_called_once_with(expected_url, headers=headers, json=json_data)


@pytest.mark.parametrize(
    "api_endpoint,path,headers,json_data,expected_url",
    [
        (
            "http://api-lb:8080",
            "test",
            {"Authorization": "Bearer token"},
            {"key": "value"},
            "http://api-lb:8080/test",
        ),
        (
            "http://api-lb:8080///",
            "test/path",
            {"Authorization": "Bearer token"},
            {"data": [1, 2, 3]},
            "http://api-lb:8080/test/path",
        ),
    ],
)
def test_make_put_request(api_endpoint, path, headers, json_data, expected_url):
    """Test PUT request formation with various parameters."""
    with patch("httpx.put") as mock_put:
        mock_put.return_value = httpx.Response(200)
        _make_put_request(api_endpoint, path, headers, json_data)
        mock_put.assert_called_once_with(expected_url, headers=headers, json=json_data)
