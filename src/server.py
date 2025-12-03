# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# CORS — чтобы фронтенд на другом порту мог делать запрос
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # или ["*"] для тестов
    allow_methods=["*"],
    allow_headers=["*"],
)

class NameRequest(BaseModel):
    text: str
    smartMood: bool

@app.post("/api/names")
async def generate_names(req: NameRequest):
    prompt = build_prompt(req.text, req.smartMood)
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:7b",
                "prompt": prompt,
                "max_tokens": 200,   # ограничение длины
                "temperature": 0.7,
                "stream": False
            },
            timeout=60  # или больше, если требуется
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama request error: {e}")

    data = resp.json()
    print("Ответ Ollama:", data)
    # Обычно в ответе есть поле "response" или аналог
    text_response = data.get("response", "")
    if not isinstance(text_response, str):
        raise HTTPException(status_code=500, detail="Invalid response format from LLM")

    return {"result": text_response}


def build_prompt(text: str, smart_mood: bool) -> str:
    """
    Генерирует 5 русских названий проекта.
    smart_mood=True  — креативные, образные, метафоричные, красивые
    smart_mood=False — простые, понятные, прямые
    """

    if smart_mood:
        return (
            "Придумай 5 красивых и креативных русских названий для проекта.\n"
            "Требования:\n"
            "- Названия должны быть понятными, звучать современно и логично.\n"
            "- Можно использовать метафоры и образы, но избегай бессмысленных неологизмов.\n"
            "- Названия должны отражать идею проекта: " + text + "\n"
            "- Примеры стиля: 'Глобус Идей', 'Маршрут Знаний', 'Дороги Открытий'\n"
            "- Выведи только список, без объяснений\n"
            "Формат:\n1. Название\n2. Название\n3. Название\n4. Название\n5. Название"
        )
    else:
        return (
            "Придумай 5 простых и понятных русских названий проекта.\n"
            "Требования:\n"
            "- Названия должны быть короткими, прямыми и ясными.\n"
            "- Не использовать сложные метафоры или абстракции.\n"
            "- Выведи только список, без объяснений\n"
            "Идея проекта: " + text + "\n"
            "Формат:\n1. Название\n2. Название\n3. Название\n4. Название\n5. Название"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001, reload=True)
