import pytest
from requests import Response
from requests.exceptions import HTTPError

from wallaroo.exceptions import (
    APIErrorResponse,
    InferenceError,
    InferenceTimeoutError,
    WallarooAPIError,
    handle_errors,
)


# Fixtures
@pytest.fixture
def mock_response(mocker):
    response = mocker.Mock(spec=Response)
    response.status_code = 400
    return response


@pytest.fixture
def json_error_response(mock_response):
    mock_response.json.return_value = {
        "code": 400,
        "status": "error",
        "error": "Bad Request",
        "source": "engine",
    }
    return mock_response


# Test APIErrorResponse
@pytest.mark.parametrize(
    "response_data, expected",
    [
        (
            {
                "code": 429,
                "status": "Error",
                "error": "no available capacity",
                "source": "engine",
            },
            {
                "code": 429,
                "status": "Error",
                "error": "no available capacity",
                "source": "engine",
            },
        ),
        (
            {"status": "error"},  # Partial data
            {"code": 400, "status": "error", "error": None, "source": None},
        ),
    ],
)
def test_api_error_response_from_response_with_json(
    mock_response, response_data, expected
):
    mock_response.json.return_value = response_data
    error_response = APIErrorResponse.from_response(mock_response)

    assert error_response.code == expected["code"]
    assert error_response.status == expected["status"]
    assert error_response.error == expected["error"]
    assert error_response.source == expected["source"]
    assert error_response.original_response == mock_response


def test_api_error_response_from_response_with_non_json(mock_response):
    mock_response.json.side_effect = ValueError
    mock_response.text = "Plain text error"

    error_response = APIErrorResponse.from_response(mock_response)

    assert error_response.code == mock_response.status_code
    assert error_response.error == "Plain text error"
    assert error_response.original_response == mock_response


# Add a test for empty JSON response
def test_api_error_response_with_empty_json(mock_response):
    mock_response.json.return_value = {}
    error_response = APIErrorResponse.from_response(mock_response)

    assert error_response.code == mock_response.status_code
    assert error_response.status is None
    assert error_response.error is None
    assert error_response.source is None


# Add a test for missing keys in JSON response
def test_api_error_response_with_missing_keys(mock_response):
    mock_response.json.return_value = {"status": "error"}
    error_response = APIErrorResponse.from_response(mock_response)

    assert error_response.code == mock_response.status_code
    assert error_response.status == "error"
    assert error_response.error is None
    assert error_response.source is None


# Test WallarooAPIError
def test_wallaroo_api_error_str_format(json_error_response):
    error_response = APIErrorResponse.from_response(json_error_response)
    error = WallarooAPIError(error_response)

    expected_str = "[400] Bad Request (source: engine, status: error)"
    assert str(error) == expected_str


def test_wallaroo_api_error_with_prefix(json_error_response):
    error_response = APIErrorResponse.from_response(json_error_response)
    error = WallarooAPIError(error_response, prefix="Test Error")

    expected_str = "Test Error: [400] Bad Request (source: engine, status: error)"
    assert str(error) == expected_str


# Test handle_errors decorator
def test_handle_errors_successful_execution():
    @handle_errors()
    def successful_function():
        return "success"

    assert successful_function() == "success"


def test_handle_errors_with_custom_error_class(json_error_response):
    http_error = HTTPError(response=json_error_response)

    @handle_errors(http_error_class=InferenceError)
    def failing_function():
        raise http_error

    with pytest.raises(InferenceError) as exc_info:
        failing_function()

    assert exc_info.value.code == 400
    assert "Inference failed" in str(exc_info.value)


# Test InferenceError
def test_inference_error(json_error_response):
    error = InferenceError(json_error_response)

    assert error.code == 400
    assert error.error == "Bad Request"
    assert "Inference failed" in str(error)


# Test InferenceTimeoutError
def test_inference_timeout_error():
    error = InferenceTimeoutError("Connection timed out")

    assert str(error) == "Inference failed: Connection timed out"


@pytest.mark.parametrize(
    "error_msg",
    [
        "Connection timed out",
        "Network unreachable",
        "",
    ],
)
def test_inference_timeout_error_messages(error_msg):
    error = InferenceTimeoutError(error_msg)
    expected_msg = f"Inference failed: {error_msg}"

    assert str(error) == expected_msg
