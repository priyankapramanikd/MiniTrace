
from pathlib import Path

from main import read_logs, analyze_logs, filter_logs, generate_report


def test_analyze_logs_counts_correctly():
    logs = [
        "INFO Application started",
        "WARNING High memory usage",
        "ERROR Database failed",
        "ERROR Service unavailable"
    ]

    result = analyze_logs(logs)

    assert result == {
        "INFO": 1,
        "WARNING": 1,
        "ERROR": 2
    }


def test_filter_only_error_logs():
    logs = [
        "INFO Application started",
        "ERROR Database failed",
        "WARNING Slow response"
    ]

    result = filter_logs(logs, level="ERROR")

    assert result == ["ERROR Database failed"]


def test_keyword_search_is_case_insensitive():
    logs = [
        "INFO Database connected",
        "ERROR Database failed",
        "INFO Application started"
    ]

    result = filter_logs(logs, keyword="database")

    assert len(result) == 2


def test_read_logs_ignores_blank_lines(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "INFO Started\n\nERROR Failed\n",
        encoding="utf-8"
    )

    result = read_logs(log_file)

    assert result == ["INFO Started", "ERROR Failed"]


def test_generate_report_contains_summary(tmp_path):
    logs = [
        "INFO Application started",
        "ERROR Database failed"
    ]

    summary = analyze_logs(logs)
    report_file = tmp_path / "report.txt"

    generate_report(logs, summary, report_file)

    report = report_file.read_text(encoding="utf-8")

    assert "Total log entries: 2" in report
    assert "INFO: 1" in report
    assert "ERROR: 1" in report
    assert "ERROR Database failed" in report
