import pytest
import os
import sys
import json
import time


def calculate_points(report_path, assignment_type):
    weights = {
        "basic": {"test_ping": 3, "test_crud_flow": 7},
        "advanced": {"test_external_weather_integration": 8, "test_history_in_db": 10}
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

    # Безопасное получение списка тестов
    tests = data.get('tests', [])
    print(f"DEBUG: Pytest нашел следующие тесты: {[t.get('nodeid') for t in tests]}")

    for test in tests:
        nodeid = test.get('nodeid', '')
        test_name = nodeid.split('::')[-1]
        if test.get('outcome') == 'passed':
            score += current_weights.get(test_name, 0)

    return score


def main():
    assignment = os.getenv("ASSIGNMENT_TYPE", "basic").lower()
    report_file = "report.json"
    output_path = "/app/reports/results.json"

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
    finally:
        # ЗАПИСЫВАЕМ РЕЗУЛЬТАТ В ЛЮБОМ СЛУЧАЕ
        print(f"DEBUG: Попытка записи результата в {output_path}...")
        try:
            with open(output_path, 'w') as f:
                json.dump({"score": total_points}, f)
                f.flush()
                os.fsync(f.fileno())  # Принудительно пишем на диск

            if os.path.exists(output_path):
                print(f"SUCCESS: Файл {output_path} успешно создан.")
            else:
                print(f"ERROR: Файл {output_path} почему-то не создался!")
        except Exception as e:
            print(f"DEBUG: Не удалось записать results.json: {e}")

    # Небольшая пауза, чтобы Docker успел зафиксировать изменения
    time.sleep(1)
    sys.exit(0)


if __name__ == "__main__":
    main()