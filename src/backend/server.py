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
        return (
            f"Ты профессиональный нейминг-специалист. Придумай 5 современных, технологичных и стильных русских названий для IT-проекта на тему: '{text}'.\n\n"
            "ТРЕБОВАНИЯ К НАЗВАНИЯМ:\n"
            "1. МАКСИМУМ 2 слова\n"
            "2. Названия должны звучать современно, технологично и профессионально\n"
            "3. Можно использовать английские слова в транслитерации или сочетания с русскими\n"
            "4. Избегай фентези-метафор, сказочных и поэтических образов\n"
            "5. Названия должны подходить для мобильного приложения, SaaS-платформы или IT-стартапа\n\n"
            "ПРИМЕРЫ ХОРОШИХ ТЕХНОЛОГИЧНЫХ НАЗВАНИЙ:\n"
            "- Travel Mind\n"
            "- Trip Genius\n"
            "- Умные Маршруты\n"
            "- Цифровой Гид\n"
            "- Пространство Путешествий\n\n"
            "НЕПОДХОДЯЩИЕ СТИЛИ:\n"
            "- Фентези (Эльфы, Драконы, Магия)\n"
            "- Поэзия (Шёпот Ветра, Сад Тайн)\n"
            "- Слишком абстрактные метафоры\n\n"
            "ФОРМАТ ОТВЕТА:\n"
            "Только 5 названий, каждое на новой строке, без номеров и точек."
        )
    else:
        return (
            f"Придумай 5 простых, понятных и практичных русских названий для IT-проекта на тему: '{text}'.\n"
            "ТРЕБОВАНИЯ:\n"
            "- Максимум 2 слова в названии\n"
            "- Короткие и ясные названия\n"
            "- Отражают суть проекта\n"
            "Формат: только названия, каждое на новой строке."
        )

def parse_llm_response(response_text: str) -> list:
    """Очищает ответ от модели и извлекает названия"""
    if not response_text:
        return []
    
    lines = response_text.strip().split('\n')
    clean_names = []
    
    for line in lines:
        line = line.strip()
        
        # Пропускаем строки, которые выглядят как комментарии
        if any(x in line.lower() for x in ['пример', 'например', 'как:', 'также', 'можно']):
            continue
        
        # Убираем нумерацию и маркеры
        line = re.sub(r'^[0-9]+[\.\)\-\:\s]*', '', line)
        line = re.sub(r'^[\-\*\•\>\s]+', '', line)
        
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

def improve_names_quality(names: list, smart_mood: bool) -> list:
    """Улучшает качество сгенерированных названий"""
    improved = []
    for name in names:
        name = name.strip()
        
        # Убираем только действительно странные символы, но сохраняем нормальные
        name = re.sub(r'[^\w\s\-А-Яа-яЁё]', '', name)
        
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

def generate_high_quality_fallback(text: str, smart_mood: bool) -> list:
    """Качественные fallback-названия (максимум 2 слова)"""
    if smart_mood:
        # Только 1-2 слова
        templates = [
            "Горизонт Мечты",
            "Шёпот Ветра",
            "Карта Судьбы",
            "Путь Звёзд",
            "Сад Тайн",
            "Мост Мечты",
            "Река Времени",
            "Окно В Мир",
            "Ветер Перемен",
            "Свет Пути"
        ]
        # Адаптируем под тему
        result = []
        for i, template in enumerate(templates[:5]):
            # Немного адаптируем под тему, если это уместно
            if i == 0:
                result.append(f"Горизонт {text}")
            elif i == 1:
                result.append(f"Шёпот {text}а")
            elif i == 2:
                result.append(f"Карта {text}а")
            elif i == 3:
                result.append(f"Путь {text}а")
            else:
                result.append(f"Сад {text}ов")
        return result
    else:
        # Простые варианты (1-2 слова)
        return [
            f"Проект {text}",
            f"Мир {text}а",
            f"Карта {text}а",
            f"Путь {text}а",
            f"Система {text}"
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
                "max_tokens": 120,
                "temperature": 0.7 if smart_mood else 0.4,
                "top_p": 0.9,
                "stream": False
            },
            timeout=30
        )
        resp.raise_for_status()
    except requests.RequestException:
        fallback_names = generate_high_quality_fallback(text, smart_mood)
        # Фильтруем fallback-названия тоже по количеству слов
        return filter_by_word_count(fallback_names, max_words=2)[:5]
    
    data = resp.json()
    raw_response = data.get("response", "")
    names = parse_llm_response(raw_response)
    
    # Улучшаем качество названий
    names = improve_names_quality(names, smart_mood)
    
    # Фильтруем по количеству слов (максимум 2)
    names = filter_by_word_count(names, max_words=2)
    
    # Если мало хороших названий, добавляем fallback
    if len(names) < 3:
        fallback = generate_high_quality_fallback(text, smart_mood)
        fallback = filter_by_word_count(fallback, max_words=2)
        # Объединяем, избегая дубликатов
        all_names = names + [n for n in fallback if n not in names]
        names = all_names[:5]
    
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