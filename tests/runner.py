import json
import os
import sys
import time

import pytest


def calculate_points(report_path, assignment_type):
    weights = {
        "basic": {"test_ping": 3, "test_crud_flow": 7},
        "advanced": {"test_ping": 2, "test_external_weather_integration": 6, "test_history_in_db": 10},
    }

    if not os.path.exists(report_path):
        return 0

    try:
        with open(report_path, "r") as f:
            data = json.load(f)
    except Exception:
        return 0

    score = 0
    current_weights = weights.get(assignment_type, {})

    tests = data.get("tests", [])
    for test in tests:
        nodeid = test.get("nodeid", "")
        test_name = nodeid.split("::")[-1]
        if test.get("outcome") == "passed":
            score += current_weights.get(test_name, 0)

    return score


def main():
    assignment = os.getenv("ASSIGNMENT_TYPE", "basic").lower()
    report_file = "/app/report.json"
    output_path = "/app/results.json"

    total_points = 0
    exit_code = 2

    try:
        test_path = f"tests/{assignment}_tests.py"

        exit_code = pytest.main(
            [
                test_path,
                "-q",
                "--json-report",
                f"--json-report-file={report_file}",
            ]
        )

        total_points = calculate_points(report_file, assignment)
        print(f"Набрано баллов: {total_points}")

        result_data = {"score": total_points, "assignment": assignment}

        with open(output_path, "w") as f:
            json.dump(result_data, f)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        exit_code = 2

    time.sleep(1)

    if exit_code in (0, 1):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
