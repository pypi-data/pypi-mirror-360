# tests/test_checker.py
from unittest.mock import MagicMock

import pytest
import requests

# Import the function we want to test using an absolute import
from simple_http_checker.checker import check_urls


@pytest.fixture
def mock_requests_get(mocker):
    """Fixture to mock requests.get, returning the mock object."""
    return mocker.patch("simple_http_checker.checker.requests.get")


def test_check_urls_success(mock_requests_get):
    """Test the case where a URL returns a 200 OK status."""
    # Configure the mock to return a successful response object
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_response.ok = True
    mock_requests_get.return_value = mock_response

    urls = ["https://google.com"]
    results = check_urls(urls)

    # Assertions
    mock_requests_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == "200 OK"


def test_check_urls_client_error(mock_requests_get):
    """Test the case where a URL returns a 404 Not Found error."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mock_response.ok = False
    mock_requests_get.return_value = mock_response

    urls = ["http://example.com/nonexistent"]
    results = check_urls(urls)

    mock_requests_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == "404 Not Found"


@pytest.mark.parametrize(
    "error_exception, expected_status",
    [
        (requests.exceptions.Timeout, "TIMEOUT"),
        (requests.exceptions.ConnectionError, "CONNECTION_ERROR"),
        (requests.exceptions.RequestException, "REQUEST_ERROR: RequestException"),
    ],
    ids=["timeout", "connection_error", "other_request_error"],
)
def test_check_urls_request_exceptions(
    mock_requests_get, error_exception, expected_status
):
    """Test handling of various requests exceptions."""
    # Configure the mock to raise the specified exception when called
    mock_requests_get.side_effect = error_exception(f"Simulated {expected_status}")

    urls = ["http://test.url"]
    results = check_urls(urls)

    mock_requests_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == expected_status


def test_check_urls_with_multiple_urls(mock_requests_get):
    """Test checking multiple URLs with different outcomes."""
    # Configure different return values for subsequent calls
    mock_response_ok = MagicMock(status_code=200, reason="OK", ok=True)
    mock_response_fail = MagicMock(status_code=500, reason="Server Error", ok=False)

    mock_requests_get.side_effect = [
        mock_response_ok,
        requests.exceptions.Timeout("Simulated timeout"),
        mock_response_fail,
    ]

    urls = ["http://success.com", "http://timeout.com", "http://fail.com"]
    results = check_urls(urls)

    assert len(results) == 3
    assert results["http://success.com"] == "200 OK"
    assert results["http://timeout.com"] == "TIMEOUT"
    assert results["http://fail.com"] == "500 Server Error"
    assert mock_requests_get.call_count == 3


def test_check_urls_empty_list():
    """Test that an empty list of URLs returns an empty dictionary."""
    results = check_urls([])
    assert results == {}
