import pytest
import os
import sys
import json


def calculate_points(report_path, assignment_type):
    weights = {
        "basic": {"test_ping": 3, "test_crud_flow": 7},
        "advanced": {"test_ping": 2, "test_external_weather_integration": 8, "test_history_in_db": 10}
    }

    if not os.path.exists(report_path):
        return 0

    with open(report_path, 'r') as f:
        data = json.load(f)

    score = 0
    current_weights = weights.get(assignment_type, {})

    for test in data.get('tests', []):
        test_name = test['nodeid'].split('::')[-1]
        if test['outcome'] == 'passed':
            score += current_weights.get(test_name, 0)
    return score


def main():
    assignment = os.getenv("ASSIGNMENT_TYPE", "basic").lower()
    report_file = "report.json"

    output_path = "/app/results.json"

    test_path = f"tests/{assignment}_tests.py"

    pytest.main([
        test_path,
        "-q",
        f"--json-report",
        f"--json-report-file={report_file}"
    ])

    total_points = calculate_points(report_file, assignment)

    with open(output_path, 'w') as f:
        json.dump({"score": total_points}, f)


    sys.exit(0)


if __name__ == "__main__":
    main()