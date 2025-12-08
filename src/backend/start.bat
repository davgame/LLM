@echo off
chcp 65001 >nul
color 0A
title 🚀 Генератор названий проектов

echo ============================================
echo          ЗАПУСК ГЕНЕРАТОРА НАЗВАНИЙ
echo ============================================
echo.

echo 1. 📍 Текущая папка: %cd%
echo.

echo 2. 🔧 Проверяю Python...
python --version >nul 2>nul
if errorlevel 1 (
    echo    ❌ Python не установлен!
    echo    📥 Открываю сайт для скачивания...
    start https://www.python.org/downloads/
    echo.
    echo    Установите Python 3.8+ и запустите снова
    pause
    exit
)
echo    ✅ Python установлен
echo.

echo 3. 📦 Проверяю виртуальное окружение...
if not exist "virtual\.venv\" (
    echo    ⚠  Виртуальное окружение не найдено
    echo    📥 Создаю...
    cd virtual
    uv venv .venv
    cd ..
    echo    ✅ Виртуальное окружение создано
) else (
    echo    ✅ Виртуальное окружение уже существует
)
echo.

echo 4. 📥 Активирую окружение и проверяю зависимости...
cd virtual
call .venv\Scripts\activate.bat
cd ..

python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo    ⚠  Устанавливаю зависимости...
    cd virtual
    call .venv\Scripts\activate.bat
    uv pip install fastapi uvicorn requests pydantic --quiet
    cd ..
    echo    ✅ Зависимости установлены
) else (
    echo    ✅ Зависимости уже установлены
)
echo.

echo 5. 🤖 Проверяю Ollama...
where ollama >nul 2>nul
if errorlevel 1 (
    echo    ❌ Ollama не найден!
    echo.
    echo    📥 Скачайте и установите Ollama:
    echo    https://ollama.com
    echo.
    echo    ⏸  Запуск приостановлен...
    pause
    exit
)
echo    ✅ Ollama найден
echo.

echo 6. 🔍 Проверяю запущен ли Ollama...
timeout /t 1 /nobreak >nul
python -c "import requests; r = requests.get('http://localhost:11434/api/tags', timeout=2); exit(0) if r.status_code == 200 else exit(1)" 2>nul
if errorlevel 1 (
    echo    ⚠  Ollama не запущен
    echo    🚀 Запускаю...
    start /B cmd /c "ollama serve"
    timeout /t 5 /nobreak >nul
    echo    ✅ Ollama запущен
) else (
    echo    ✅ Ollama уже запущен
)
echo.

echo 7. 🧠 Проверяю модель Qwen2.5:7b...
ollama list | findstr "qwen2.5:7b" >nul
if errorlevel 1 (
    echo    ⚠  МОДЕЛЬ НЕ НАЙДЕНА!
    echo.
    echo    📦 Для работы нужна модель Qwen2.5:7b (4.6 ГБ)
    echo    ⏳ Время загрузки: 5-20 минут
    echo.
    echo    ❓ Хотите установить модель сейчас?
    echo       [Y] Да, установить и продолжить
    echo       [N] Нет, продолжить без модели
    echo       [I] Установить отдельно (через install_model.bat)
    echo.
    choice /c YNI /n /m "Ваш выбор (Y/N/I): "
    
    if errorlevel 3 (
        echo    ℹ  Запустите install_model.bat для установки модели
        timeout /t 3
        echo    ⏸  Запуск приостановлен...
        pause
        exit
    )
    
    if errorlevel 2 (
        echo    ⚠  Продолжаю БЕЗ модели
        echo    💡 API будет возвращать ошибки
        goto SKIP_MODEL
    )
    
    if errorlevel 1 (
        echo    ⬇️  Начинаю загрузку модели...
        echo    ⏳ Пожалуйста, подождите...
        ollama pull qwen2.5:7b
        echo    ✅ Модель установлена!
    )
) else (
    echo    ✅ Модель уже установлена
)

:SKIP_MODEL
echo.
echo ============================================
echo            🎉 ВСЁ ГОТОВО!
echo ============================================
echo.
echo 🌐 API сервер запускается:
echo 📍 http://localhost:3001
echo.
echo 📚 Документация:
echo 📍 http://localhost:3001/docs
echo.
echo 💡 Пример запроса:
echo {
echo   "text": "образовательная платформа",
echo   "smartMood": true
echo }
echo.
echo ⚠  НЕ ЗАКРЫВАЙТЕ ЭТО ОКНО
echo 🛑 Для остановки нажмите Ctrl+C
echo ============================================
echo.

virtual\.venv\Scripts\python.exe server.py