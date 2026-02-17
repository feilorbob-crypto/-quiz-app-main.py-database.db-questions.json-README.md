#!/usr/bin/env python3
"""Конвертер текстового блока вопросов в JSON-массив для quiz-программы.

Читает сырой текст из stdin и печатает только JSON-массив в stdout.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Dict, List, Tuple

QUESTION_START_RE = re.compile(r"^\s*(\d+)[\).]\s*(.+?)\s*$")
OPTION_RE = re.compile(r"^\s*([A-DА-Гa-dа-г])[\).:\-]\s*(.+?)\s*$")
CORRECT_RE = re.compile(
    r"^\s*(?:правильн(?:ый|ого)\s*ответ|ответ|correct(?:\s*answer)?)\s*[:\-]?\s*([A-DА-Гa-dа-г1-4])\s*$",
    re.IGNORECASE,
)

LETTER_TO_INDEX = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "А": 0,
    "Б": 1,
    "В": 2,
    "Г": 3,
}


def normalize_letter(token: str) -> str:
    return token.strip().upper()


def parse_correct_index(token: str) -> int:
    normalized = normalize_letter(token)
    if normalized.isdigit():
        value = int(normalized)
        return value - 1 if 1 <= value <= 4 else -1
    return LETTER_TO_INDEX.get(normalized, -1)


def finalize_question(question: str, options_map: Dict[int, str], correct_index: int) -> Dict[str, object]:
    options = [options_map.get(i, "") for i in range(4)]
    return {
        "question": question.strip(),
        "options": options,
        "correct_index": correct_index if 0 <= correct_index <= 3 else -1,
        "explanation": "",
    }


def convert(raw: str) -> List[Dict[str, object]]:
    lines = [line.rstrip() for line in raw.splitlines()]
    results: List[Dict[str, object]] = []

    current_question: str | None = None
    current_options: Dict[int, str] = {}
    current_correct = -1

    for line in lines:
        if not line.strip():
            continue

        q_match = QUESTION_START_RE.match(line)
        if q_match:
            if current_question is not None:
                results.append(finalize_question(current_question, current_options, current_correct))
            current_question = q_match.group(2)
            current_options = {}
            current_correct = -1
            continue

        opt_match = OPTION_RE.match(line)
        if opt_match and current_question is not None:
            idx = parse_correct_index(opt_match.group(1))
            if 0 <= idx <= 3:
                current_options[idx] = opt_match.group(2).strip()
            continue

        corr_match = CORRECT_RE.match(line)
        if corr_match and current_question is not None:
            current_correct = parse_correct_index(corr_match.group(1))
            continue

        # Продолжение текста вопроса, если встретилась дополнительная строка.
        if current_question is not None and len(current_options) == 0:
            current_question = f"{current_question} {line.strip()}".strip()

    if current_question is not None:
        results.append(finalize_question(current_question, current_options, current_correct))

    return results


def main() -> None:
    raw = sys.stdin.read()
    converted = convert(raw)
    sys.stdout.write(json.dumps(converted, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
