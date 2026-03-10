import pytest
import os
import sys

def main():
    assignment = os.getenv("ASSIGNMENT_TYPE", "basic").lower()
    base_url = os.getenv("BASE_URL", "http://student-app:8080")

    print(f"Начинаем проверку задания: {assignment.upper()}")
    print(f"Целевой URL: {base_url}")

    if assignment == "basic":
        test_path = "tests/basic_tests.py"
        max_score = 10
    elif assignment == "advanced":
        test_path = "tests/advanced_tests.py"
        max_score = 20
    else:
        print(f"Ошибка: Неизвестный тип задания '{assignment}'")
        sys.exit(1)

    retcode = pytest.main([test_path, "-q", "--tb=short"])

    if retcode == 0:
        print("Все тесты пройдены!")
        print(f"POINTS: {max_score}")
        sys.exit(0)
    else:
        print("Тесты завалены. Попробуй еще раз.")
        print("POINTS: 0")
        sys.exit(retcode)

if __name__ == "__main__":
    main()