from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import subprocess
import sys
import time
import threading
from functools import lru_cache
import re

app = FastAPI(title="Генератор названий проектов")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def start_ollama_in_background():
    """Запуск Ollama в фоновом режиме при старте сервера"""
    def run():
        try:
            requests.get("http://localhost:11434/api/tags", timeout=2)
            print("✅ Ollama уже запущен")
            return
        except:
            print("🔄 Запускаю Ollama...")
            if sys.platform == "win32":
                subprocess.Popen(
                    ['ollama', 'serve'],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                subprocess.Popen(
                    ['ollama', 'serve'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            for i in range(30):
                try:
                    requests.get("http://localhost:11434/api/tags", timeout=2)
                    print("✅ Ollama успешно запущен")
                    return
                except:
                    time.sleep(1)
            
            print("❌ Не удалось запустить Ollama")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

# Запускаем Ollama при старте
start_ollama_in_background()

class NameRequest(BaseModel):
    text: str
    smartMood: bool

def build_prompt(text: str, smart_mood: bool) -> str:
    if smart_mood:
        return f"""
ЗАДАЧА:
Сгенерируй 5 названий для IT-проекта.

ТЕМА:
{text}

ЖЁСТКИЕ ТРЕБОВАНИЯ:
- Только русский язык
- Запрещены английские слова, латиница и транслитерация
- Максимум 2 слова в названии
- Современный, технологичный стиль
- Подходит для стартапа, SaaS или приложения
- Без метафор, поэзии и абстракций

ФОРМАТ ОТВЕТА:
- Ровно 5 строк
- Без нумерации
- Без пояснений
- Только названия

ПРИМЕРЫ:

Вход: путешествия
Выход:
Умные Маршруты
Цифровой Гид
Планер Поездок
Карта Путей
Сервис Поездок

Вход: задачи
Выход:
Менеджер Задач
Планировщик Дел
Контроль Задач
Список Дел
Трекер Задач

СГЕНЕРИРУЙ:

Вход: {text}
Выход:
"""
    else:
        return f"""
ЗАДАЧА:
Придумай 5 названий для проекта.

ТЕМА:
{text}

ТРЕБОВАНИЯ:
- Только русский язык
- Максимум 2 слова
- Простые и понятные названия
- Отражают суть проекта

ФОРМАТ:
- 5 строк
- Без пояснений
- Без нумерации

Вход: {text}
Выход:
"""

def parse_llm_response(response_text: str) -> list:
    """Очищает ответ от модели и извлекает названия"""
    if not response_text:
        return []
    
    lines = response_text.strip().split('\n')
    clean_names = []
    
    for line in lines:
        line = line.strip()
        
        # убираем нумерацию
        line = re.sub(r'^[0-9]+[\.\)\-\:\s]*', '', line)

        # убираем маркеры
        line = re.sub(r'^[\-\*\•\>\s]+', '', line)

        # потом чистим символы
        line = re.sub(r'[^\w\s\-А-Яа-яЁё0-9]', '', line)
        
        # Убираем кавычки и лишние пробелы
        line = line.strip('"\'«»')
        line = re.sub(r'\s+', ' ', line)
        
        # Проверяем, что название не слишком длинное
        if 2 <= len(line) <= 50:
            clean_names.append(line)
    
    return clean_names

def filter_by_word_count(names: list, max_words: int = 2) -> list:
    """Фильтрует названия по количеству слов"""
    filtered = []
    for name in names:
        # Подсчитываем количество слов
        word_count = len(name.split())
        if 1 <= word_count <= max_words:
            filtered.append(name)
    return filtered

def is_russian(text: str) -> bool:
    return bool(re.search(r'[А-Яа-яЁё]', text))

def improve_names_quality(names: list, smart_mood: bool) -> list:
    """Улучшает качество сгенерированных названий"""
    improved = []
    for name in names:
        name = name.strip()
        
        # Убираем только действительно странные символы, но сохраняем нормальные
        name = re.sub(r'[^\w\s\-А-Яа-яЁё0-9]', '', name)
        
        # Для Smart Mode: исправляем слипшиеся слова
        if smart_mood:
            # Разделяем слипшиеся слова с заглавной буквы
            name = re.sub(r'([а-яё])([А-ЯЁ])', r'\1 \2', name)
            name = re.sub(r'([а-яё])([А-ЯЁ][а-яё]+)', r'\1 \2', name)
        
        # Убираем лишние пробелы
        name = re.sub(r'\s+', ' ', name)
        
        # Проверяем длину и количество слов
        words = name.split()
        if 1 <= len(words) <= 2 and len(name) >= 2 and len(name) <= 30:
            improved.append(name)
    
    # Убираем дубликаты
    seen = set()
    unique_improved = []
    for name in improved:
        if name.lower() not in seen:
            seen.add(name.lower())
            unique_improved.append(name)
    
    return unique_improved[:5]

def score_name(name):
    score = 0
    if len(name.split()) == 2:
        score += 2
    if len(name) < 20:
        score += 1
    if name[0].isupper():
        score += 1
    return score

def generate_high_quality_fallback(text: str, smart_mood: bool) -> list:
    base = text.capitalize()
    return [
        f"{base} Платформа",
        f"{base} Сервис",
        f"{base} Система",
        f"{base} Решения",
        f"{base} Центр"
    ]

@lru_cache(maxsize=100)
def generate_names_cached(text: str, smart_mood: bool) -> list:
    """Кэшированная генерация названий с улучшенным качеством"""
    
    prompt = build_prompt(text, smart_mood)

    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:7b",
                "prompt": prompt,
                "max_tokens": 200,
                "temperature": 0.4,
                "top_p": 0.8,
                "repeat_penalty": 1.2,
                "stream": False
            },
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        raw_response = data.get("response", "").strip()
        print("RAW FROM MODEL:", raw_response)

    except requests.RequestException:
        # если ошибка запроса → fallback
        fallback = generate_high_quality_fallback(text, smart_mood)
        return filter_by_word_count(fallback, max_words=2)[:5]

    # ❗ если модель ничего не вернула
    if not raw_response:
        fallback = generate_high_quality_fallback(text, smart_mood)
        return filter_by_word_count(fallback, max_words=2)[:5]

    # ✅ парсим
    names = parse_llm_response(raw_response)

    # ✅ улучшаем
    names = improve_names_quality(names, smart_mood)

    # ✅ фильтр по словам
    names = filter_by_word_count(names, max_words=2)

    names = [n for n in names if is_russian(n)]
    names = sorted(names, key=score_name, reverse=True)

    # ❗ если мало нормальных
    if len(names) < 5:
        fallback = generate_high_quality_fallback(text, smart_mood)
        fallback = filter_by_word_count(fallback, max_words=2)
        names = list(dict.fromkeys(names + fallback))

    return names[:5]

@app.get("/api/test")
async def test():
    return {"status": "ok", "data": "Данные с бэкенда"}

@app.post("/api/names")
async def generate_names(req: NameRequest):
    names = generate_names_cached(req.text, req.smartMood)
    return {"result": names}

@app.get("/")
async def root():
    return {
        "message": "Генератор названий проектов",
        "model": "my-naming-model",  #Объединенная модель Qwen 2.5 7b + LoRa-адаптер
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

def run_server():
    """Запуск сервера с подробной информацией"""
    import uvicorn
    print("=" * 50)
    print("🚀 Генератор названий проектов")
    print("🌐 Сервер запущен: http://localhost:3001")
    print("📚 Документация: http://localhost:3001/docs")
    print("⚡ Эндпоинты: /api/test, /api/names, /health")
    print("=" * 50)
    
    uvicorn.run("server:app", host="0.0.0.0", port=3001, reload=True)

if __name__ == "__main__":
    run_server()