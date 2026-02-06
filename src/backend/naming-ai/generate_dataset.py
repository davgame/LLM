import json
import random

SYSTEM_PROMPT = "Ты — AI для генерации названий стартапов. Дай одно короткое, креативное, брендируемое название."

CATEGORIES = [
    "CRM система для малого бизнеса",
    "Платформа онлайн-обучения",
    "Финансовый трекер расходов",
    "Сервис управления подписками",
    "Приложение для фитнеса",
    "Маркетинговая платформа",
    "AI помощник для бизнеса",
    "Платформа аналитики данных",
    "Сервис планирования задач",
    "Мобильный банк",
    "Платформа для фрилансеров",
    "HR система",
    "Облачное хранилище",
    "Сервис доставки еды",
    "Приложение для медитации",
    "Юридический онлайн-сервис",
    "Платформа кибербезопасности",
    "Система умного дома",
    "Сервис бронирования",
    "EdTech платформа"
]

PREFIXES = [
    "Платформа",
    "Сервис",
    "Приложение",
    "Онлайн-система",
    "Инструмент",
    "Экосистема",
    "Решение",
    "Цифровой сервис"
]


NAMES = [
    "Core", "Flow", "Nest", "Sync", "Mind", "Cloud", "Track",
    "Boost", "Link", "Base", "Hub", "Pro", "Net", "Wave", "Labs",
    "Logic", "Pilot", "Stack", "Forge", "Pulse"
]


def generate_prompt():
    base = random.choice(CATEGORIES)
    prefix = random.choice(PREFIXES)

    return f"{prefix} для {base.lower()}"


def generate_name():
    a = random.choice(NAMES)
    b = random.choice(NAMES)

    return (a + b).capitalize()


def create_sample():
    return {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": generate_prompt()
            },
            {
                "role": "assistant",
                "content": generate_name()
            }
        ]
    }


def main():
    data = []

    for _ in range(400):
        data.append(create_sample())

    with open("train.jsonl", "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("✅ Dataset created: 400 samples")


if __name__ == "__main__":
    main()
