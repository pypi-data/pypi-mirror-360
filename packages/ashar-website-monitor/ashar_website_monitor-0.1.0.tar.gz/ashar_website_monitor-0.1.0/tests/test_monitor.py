import pytest
from unittest.mock import MagicMock, patch
from src.monitor import Monitor

def test_monitor_start_calls_request_once():
    mock_site = MagicMock()
    mock_site.request.return_value = (True, 0.1)

    monitor = Monitor([mock_site], checking_period=0.01)

    with patch("time.sleep", side_effect=KeyboardInterrupt):
        monitor.start()  # we expect it to handle and exit gracefully because I already handled keyboard exception in monitor file.

    # Validate .request() was called at least once
    assert mock_site.request.called
