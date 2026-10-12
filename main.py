
from pathlib import Path

LOG_FILE = Path("sample_logs/app.log")
REPORT_FILE = Path("report.txt")


def read_logs(file_path):
    """Read non-empty lines from a log file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def analyze_logs(log_lines):
    """Count INFO, WARNING, and ERROR entries."""
    summary = {
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0
    }

    for line in log_lines:
        for level in summary:
            if level in line:
                summary[level] += 1
                break

    return summary


def filter_logs(log_lines, level=None, keyword=None):
    """Filter logs by severity and/or keyword."""
    results = []

    for line in log_lines:
        if level and level not in line:
            continue

        if keyword and keyword.lower() not in line.lower():
            continue

        results.append(line)

    return results


def generate_report(log_lines, summary, output_path):
    """Save a summary and error details to a report file."""
    errors = filter_logs(log_lines, level="ERROR")

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("===== MiniTrace Log Report =====\n")
        file.write(f"Total log entries: {len(log_lines)}\n")
        file.write(f"INFO: {summary['INFO']}\n")
        file.write(f"WARNING: {summary['WARNING']}\n")
        file.write(f"ERROR: {summary['ERROR']}\n")

        file.write("\n===== Error Details =====\n")

        for error in errors:
            file.write(error + "\n")


def main():
    logs = read_logs(LOG_FILE)
    summary = analyze_logs(logs)

    print("\n===== MiniTrace Log Summary =====")
    print(f"Total log entries: {len(logs)}")
    print(f"INFO: {summary['INFO']}")
    print(f"WARNING: {summary['WARNING']}")
    print(f"ERROR: {summary['ERROR']}")

    errors = filter_logs(logs, level="ERROR")

    print("\n===== Error Logs =====")
    for error in errors:
        print(error)

    database_logs = filter_logs(logs, keyword="database")

    print("\n===== Search: database =====")
    for entry in database_logs:
        print(entry)

    generate_report(logs, summary, REPORT_FILE)
    print(f"\nReport saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
