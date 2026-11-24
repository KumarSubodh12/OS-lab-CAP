"""Centralized CSV reporting and activity logging."""

import csv
import logging
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(ROOT, "reports")
LOG_DIR = os.path.join(ROOT, "logs")

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "activity.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def log_event(message):
    logging.info(message)


def save_csv(filename, headers, rows):
    path = os.path.join(REPORT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(headers)
        writer.writerows(rows)

    log_event(f"Report generated: {filename}")
    print(f"Saved report: {path}")
    return path


def show_recent_logs(limit=12):
    if int(limit) <= 0:
        raise ValueError("Log display limit must be greater than zero.")

    path = os.path.join(LOG_DIR, "activity.log")
    if not os.path.exists(path):
        print("No activity log found.")
        return

    with open(path, encoding="utf-8") as log_file:
        lines = log_file.readlines()

    print("----- Recent activity -----")
    print("".join(lines[-int(limit):]) or "No activity yet.")
