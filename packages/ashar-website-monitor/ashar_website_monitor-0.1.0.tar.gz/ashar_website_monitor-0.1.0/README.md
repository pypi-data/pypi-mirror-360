# Website Monitoring Tool

A Python-based website monitoring tool that periodically checks the availability and content of specified websites, logging detailed structured JSON logs and console output.

---

## Features

- Periodic checks of multiple URLs with user-defined intervals.
- Validates HTTP response status codes.
- Verifies presence of expected content in the response.
- Handles and logs connection errors, timeouts, and HTTP errors.
- Structured logging to console and JSON file with rich metadata.
- Configurable via YAML file.

---
## Project Structure

## Project Structure

```text
├── ashar_website_monitor/
│   ├── config/
│   │   └── config.yaml             # User input config for URLs and checking period
│   ├── logs/
│   │   └── monitoring_logs.json    # JSON log output
│   ├── src/
│   │   ├── logger_config.py        # Custom logger setup with JSON formatter
│   │   ├── monitor.py              # Monitor class to run periodic checks
│   │   └── website.py              # Website class to handle individual site checks
│   ├── __init__.py
│   ├── main.py                     # Main script to load config and start monitoring
├── tests/
│   ├── test_website.py             # Unit tests for Website class
│   └── test_monitor.py             # Unit tests for Monitor class
├── .gitignore                      # Git ignore file
├── pyproject.toml                  # Pip package setup file
├── requirements.txt                # Package requrements
└── README.md                       # This documentation

---

## Configuration

Create a YAML config file specifying the checking period and URLs to monitor.

Example `config/config.yaml`:

```yaml
checking_period: 7

urls:
  - url: "https://www.google.com/"
    expected_content: "Google"
  - url: "https://www.facebook.com/"
    expected_content: "ok pk hello bye"
  - url: "https://httpbin.org/status/404"
    expected_content: "hello world"
  - url: "http://thisdomaindoesnotexist1234567890.com"
    expected_content: "anything"
  - url: "https://httpbin.org/delay/10"
    expected_content: "Delayed"
  - url: "htp://invalid-url.com"
    expected_content: "test"
  - url: "https://httpbin.org/status/500"
    expected_content: "internal"
```

## Usage

### Pre requisites

- Python 3.7+
- Install dependencies:

```
pip install -r requirements.txt
```

### Run the monitor

```
python main.py --config config/config.yaml
```

### Testing

Run all tests with:

```
PYTHONPATH=./ashar_website_monitor pytest -v tests/
```


## Logging

Logs structured JSON entries containing:

- asctime (timestamp)
- url
- status_code
- response_time
- levelname
- error_type
- message

Logs are written both to console (plain text) and JSON file.

