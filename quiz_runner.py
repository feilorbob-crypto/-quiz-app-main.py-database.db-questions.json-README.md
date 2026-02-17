#!/usr/bin/env python3
"""CLI-запуск серии вопросов из questions.json с использованием exam_checker.evaluate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from exam_checker import evaluate


Question = Dict[str, Any]


def load_questions(path: Path) -> List[Question]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        questions = data
    elif isinstance(data, dict) and isinstance(data.get("questions"), list):
        questions = data["questions"]
    else:
        raise ValueError("Ожидается JSON-массив вопросов или объект с ключом 'questions'.")

    if not questions:
        raise ValueError("Список вопросов пуст.")

    return questions


def parse_answers(raw: str | None, expected_count: int) -> List[int]:
    if raw is None:
        return []

    parts = [part.strip() for part in raw.split(",") if part.strip()]
    answers: List[int] = []

    for idx, part in enumerate(parts, start=1):
        if not part.isdigit():
            raise ValueError(f"Ответ #{idx} должен быть числом, получено: {part}")
        value = int(part)
        if value < 1:
            raise ValueError(f"Ответ #{idx} должен быть >= 1, получено: {value}")
        answers.append(value - 1)

    if len(answers) > expected_count:
        raise ValueError("Передано больше ответов, чем вопросов в файле.")

    return answers


def ask_user_index(options: List[str]) -> int:
    while True:
        raw = input(f"Введите номер варианта (1-{len(options)}): ").strip()
        if not raw.isdigit():
            print("Нужно ввести целое число.")
            continue

        selected = int(raw)
        if not (1 <= selected <= len(options)):
            print("Номер вне диапазона вариантов.")
            continue

        return selected - 1


def run_quiz(questions: List[Question], predefined_answers: List[int]) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    correct_count = 0
    skipped_count = 0

    for i, item in enumerate(questions, start=1):
        question = item["question"]
        options = item["options"]
        correct_index = item.get("correct_index", -1)

        print(f"\nВопрос {i}: {question}")
        for option_idx, option in enumerate(options, start=1):
            print(f"  {option_idx}. {option}")

        if not isinstance(correct_index, int) or correct_index == -1:
            skipped_count += 1
            print("Пропуск: корректный correct_index не задан.")
            results.append(
                {
                    "question": question,
                    "skipped": True,
                    "reason": "correct_index не задан (ожидается значение 0..3)",
                    "correct_index": correct_index,
                }
            )
            continue

        if i - 1 < len(predefined_answers):
            user_index = predefined_answers[i - 1]
            if not (0 <= user_index < len(options)):
                raise ValueError(
                    f"Предопределенный ответ для вопроса {i} вне диапазона вариантов."
                )
            print(f"Выбран (из --answers): {user_index + 1}")
        else:
            user_index = ask_user_index(options)

        payload = {
            "question": question,
            "options": options,
            "correct_index": correct_index,
            "user_index": user_index,
        }

        if "source" in item:
            payload["source"] = item["source"]

        result = evaluate(payload)
        result["question"] = question
        results.append(result)

        if result["is_correct"]:
            correct_count += 1

    return {
        "total_questions": len(questions),
        "correct_answers": correct_count,
        "skipped_questions": skipped_count,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Запуск теста из questions.json с проверкой через exam_checker.py"
    )
    parser.add_argument(
        "--questions",
        default="questions.json",
        help="Путь к JSON-файлу с вопросами (по умолчанию: questions.json)",
    )
    parser.add_argument(
        "--answers",
        default=None,
        help="Опционально: ответы через запятую в 1-базной нумерации, например: 2,1,4",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Опционально: путь для сохранения итогового JSON-отчета",
    )
    args = parser.parse_args()

    questions_path = Path(args.questions)
    questions = load_questions(questions_path)
    predefined_answers = parse_answers(args.answers, len(questions))

    summary = run_quiz(questions, predefined_answers)
    rendered = json.dumps(summary, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")

    print("\nИтог:")
    print(rendered)


if __name__ == "__main__":
    main()
