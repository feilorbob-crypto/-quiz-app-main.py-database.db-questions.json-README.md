import json
import random

QUESTIONS_PATH = "data/questions.json"
QUESTIONS_COUNT = 30


def load_questions(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_quiz():
    questions = load_questions(QUESTIONS_PATH)

    if len(questions) < QUESTIONS_COUNT:
        raise ValueError("В базе меньше 30 вопросов")

    selected = random.sample(questions, QUESTIONS_COUNT)
    score = 0

    for i, q in enumerate(selected, 1):
        print(f"\nВопрос {i}: {q['question']}")
        for idx, option in enumerate(q["options"]):
            print(f"  {idx + 1}. {option}")

        while True:
            try:
                user_input = int(input("Ваш ответ (1-4): ")) - 1
                if 0 <= user_input < len(q["options"]):
                    break
            except ValueError:
                pass
            print("Введите число от 1 до 4")

        if user_input == q["correct_index"]:
            print("✔ Верно")
            score += 1
        else:
            print("✘ Неверно")

    print(f"\nРезультат: {score} из {QUESTIONS_COUNT}")


if __name__ == "__main__":
    run_quiz()

