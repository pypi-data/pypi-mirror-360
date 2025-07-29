import pytest
from unittest.mock import patch, MagicMock
from src.website import Website
import requests

@pytest.fixture
def successful_response():
    resp = MagicMock()
    resp.status_code = 200
    resp.text = "Google"
    return resp

@pytest.fixture
def client_error_response():
    resp = MagicMock()
    resp.status_code = 404
    return resp

@pytest.fixture
def server_error_response():
    resp = MagicMock()
    resp.status_code = 500
    return resp

@patch("src.website.requests.get")
def test_success_status_content_found(mock_get, successful_response):
    mock_get.return_value = successful_response
    site = Website("https://www.google.com/", expected_content="Google")
    success, resp_time = site.request()
    print(resp_time)
    assert success is True

@patch("src.website.requests.get")
def test_success_status_content_not_found(mock_get, successful_response):
    mock_get.return_value = successful_response
    site = Website("https://www.facebook.com/", expected_content="ok ok hello bye")
    success, resp_time = site.request()
    assert success is False


@patch("src.website.requests.get")
def test_client_error_status(mock_get, client_error_response):
    mock_get.return_value = client_error_response
    site = Website("https://httpbin.org/status/404", expected_content="hello world")
    success, resp_time = site.request()
    assert success is False

@patch("src.website.requests.get")
def test_server_error_status(mock_get, server_error_response):
    mock_get.return_value = server_error_response
    site = Website("https://httpbin.org/status/500", expected_content="internal")
    success, resp_time = site.request()
    assert success is False

@patch("src.website.requests.get", side_effect=requests.ConnectionError("Connection failed"))
def test_connection_error(mock_get):
    site = Website("http://thisdomaindoesnotexist1234567890.com", expected_content="anything")
    success, resp_time = site.request()
    assert success is False

@patch("src.website.requests.get", side_effect=requests.Timeout("Timeout"))
def test_timeout_error(mock_get):
    site = Website("https://httpbin.org/delay/10", expected_content="Delayed")
    success, resp_time = site.request()
    assert success is False

@patch("src.website.requests.get", side_effect=requests.RequestException("Request exception"))
def test_request_exception(mock_get):
    site = Website("htp://invalid-url.com", expected_content="test")
    success, resp_time = site.request()
    assert success is False
