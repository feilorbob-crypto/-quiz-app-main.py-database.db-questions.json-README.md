#!/usr/bin/env python3
"""Проверка ответа пользователя по уже заданному тестовому вопросу.

Скрипт принимает JSON из stdin и печатает строго JSON в stdout.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict


def _build_explanation(
    question: str,
    user_answer: str,
    correct_answer: str,
    is_correct: bool,
    source: Dict[str, Any] | None,
) -> str:
    if source is not None:
        doc_number = source.get("document_number", "")
        doc_title = source.get("document_title", "")
        clause = source.get("clause", "")
        source_text = " ".join(part for part in [doc_number, f"«{doc_title}»" if doc_title else ""] if part).strip()
        clause_text = f" в пункте {clause}" if clause else ""

        if is_correct:
            return (
                f"Ответ верный: «{correct_answer}». "
                f"Это соответствует определению{clause_text} {source_text}."
            ).strip()

        return (
            f"Правильный вариант: «{correct_answer}». "
            f"Выбранный вариант «{user_answer}» не соответствует определению, указанному{clause_text} {source_text}."
        ).strip()

    if is_correct:
        return f"Ответ верный: «{correct_answer}» логически соответствует формулировке вопроса «{question}»."

    return (
        f"Правильный вариант: «{correct_answer}». "
        f"Выбранный вариант «{user_answer}» не соответствует логике формулировки вопроса «{question}»."
    )


def evaluate(payload: Dict[str, Any]) -> Dict[str, Any]:
    question = payload["question"]
    options = payload["options"]
    correct_index = payload["correct_index"]
    user_index = payload["user_index"]
    source = payload.get("source")

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Поле 'question' должно быть непустой строкой.")

    if not isinstance(options, list) or len(options) == 0:
        raise ValueError("Поле 'options' должно быть непустым списком.")

    if not all(isinstance(opt, str) for opt in options):
        raise ValueError("Все элементы 'options' должны быть строками.")

    if not isinstance(correct_index, int) or not (0 <= correct_index < len(options)):
        raise ValueError("Поле 'correct_index' вне диапазона options.")

    if not isinstance(user_index, int) or not (0 <= user_index < len(options)):
        raise ValueError("Поле 'user_index' вне диапазона options.")

    if source is not None and not isinstance(source, dict):
        raise ValueError("Поле 'source' должно быть объектом (dict) или отсутствовать.")

    correct_answer = options[correct_index]
    user_answer = options[user_index]
    is_correct = user_index == correct_index

    result: Dict[str, Any] = {
        "is_correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "explanation": _build_explanation(
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            source=source,
        ),
    }

    if source is not None:
        result["source"] = source

    return result


def main() -> None:
    try:
        data = json.load(sys.stdin)
        result = evaluate(data)
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        error_payload = {
            "error": str(exc),
        }
        sys.stdout.write(json.dumps(error_payload, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
