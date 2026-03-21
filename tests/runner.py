import pytest
import os
import sys
import json
import time


def calculate_points(report_path, assignment_type):
    weights = {
        "basic": {"test_ping": 3, "test_crud_flow": 7},
        "advanced": {"test_ping": 2,"test_external_weather_integration": 6, "test_history_in_db": 10}
    }

    if not os.path.exists(report_path):
        print(f"DEBUG: Файл отчета {report_path} не найден!")
        return 0

    try:
        with open(report_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"DEBUG: Ошибка чтения JSON: {e}")
        return 0

    score = 0
    current_weights = weights.get(assignment_type, {})


    for test in tests:
        nodeid = test.get('nodeid', '')
        test_name = nodeid.split('::')[-1]
        if test.get('outcome') == 'passed':
            score += current_weights.get(test_name, 0)

    return score


def main():
    assignment = os.getenv("ASSIGNMENT_TYPE", "basic").lower()
    report_file = "report.json"
    output_path = "/app/results.json"  # Путь должен быть абсолютным

    total_points = 0  # Значение по умолчанию

    try:
        test_path = f"tests/{assignment}_tests.py"
        print(f"DEBUG: Запуск тестов из {test_path}")

        # Запускаем pytest
        pytest.main([
            test_path,
            "-q",
            "--json-report",
            f"--json-report-file={report_file}"
        ])

        total_points = calculate_points(report_file, assignment)
        print(f"DEBUG: Итого набрано баллов: {total_points}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")


    time.sleep(1)
    sys.exit(0)


if __name__ == "__main__":
    main()