"""Entry point for the website monitoring application, handling config loading and monitor startup."""
import yaml
import logging
from src.website import Website
from src.monitor import Monitor
from src.logger_config import setup_logger
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="Website monitoring tool")
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to the configuration YAML file"
    )
    args = parser.parse_args()

    config_path = args.config

    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    setup_logger("logs/monitoring_logs.json")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    interval = config.get("checking_period", 30)

    websites = [
        Website(item["url"], item.get("expected_content"), timeout=interval)
        for item in config.get("urls", [])
    ]

    monitor = Monitor(websites, interval)
    monitor.start()

if __name__ == "__main__":
    main()