from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import subprocess
import sys
import time

app = FastAPI(title="Генератор названий проектов")

# Разрешаем все CORS для простоты
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class NameRequest(BaseModel):
    text: str
    smartMood: bool

def start_ollama_if_needed():
    """Автозапуск Ollama если не запущен"""
    try:
        requests.get("http://localhost:11434/api/tags", timeout=2)
        print("✅ Ollama уже запущен")
        return True
    except:
        print("🔄 Запускаю Ollama...")
        if sys.platform == "win32":
            subprocess.Popen(['ollama', 'serve'], 
                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        
        for i in range(30):
            try:
                requests.get("http://localhost:11434/api/tags", timeout=2)
                print("✅ Ollama успешно запущен")
                return True
            except:
                time.sleep(1)
        
        print("❌ Не удалось запустить Ollama")
        return False

@app.post("/api/names")
async def generate_names(req: NameRequest):
    # Автозапуск Ollama
    if not start_ollama_if_needed():
        raise HTTPException(
            status_code=500, 
            detail="Не удалось запустить Ollama. Убедитесь, что он установлен."
        )
    
    prompt = build_prompt(req.text, req.smartMood)
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:7b",
                "prompt": prompt,
                "max_tokens": 200,
                "temperature": 0.7,
                "stream": False
            },
            timeout=60
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

    data = resp.json()
    return {"result": data.get("response", "")}

def build_prompt(text: str, smart_mood: bool) -> str:
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

@app.get("/")
async def root():
    return {
        "message": "Генератор названий проектов",
        "model": "Qwen2.5:7b",
        "status": "работает",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    try:
        requests.get("http://localhost:11434/api/tags", timeout=2)
        return {"status": "healthy", "ollama": "running"}
    except:
        return {"status": "degraded", "ollama": "not_running"}

def main():
    import uvicorn
    print("🚀 Запуск сервера из виртуального окружения UV...")
    print("📦 Все зависимости изолированы в .venv/")
    print("🌐 Откройте в браузере: http://localhost:3001/docs")
    uvicorn.run(app, host="0.0.0.0", port=3001, reload=True)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Сервер запущен: http://localhost:3001")
    print("📚 Документация: http://localhost:3001/docs")
    uvicorn.run("server:app", host="0.0.0.0", port=3001, reload=True)