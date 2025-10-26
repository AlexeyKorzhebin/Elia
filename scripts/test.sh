#!/bin/bash
# Скрипт запуска тестов

set -e

echo "🧪 Запуск тестов Elia AI Platform..."

# Активация виртуального окружения
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Установка Playwright браузеров (если не установлены)
if ! command -v playwright &> /dev/null; then
    echo "📥 Установка Playwright браузеров..."
    playwright install chromium
fi

# Запуск тестов
case "$1" in
    "api")
        echo "🔌 Запуск API тестов..."
        pytest -m api -v
        ;;
    "e2e")
        echo "🌐 Запуск E2E тестов..."
        pytest -m e2e -v
        ;;
    "coverage")
        echo "📊 Запуск тестов с покрытием..."
        pytest --cov=app --cov-report=html --cov-report=term
        echo "📈 Отчёт о покрытии сохранён в htmlcov/index.html"
        ;;
    *)
        echo "🎯 Запуск всех тестов..."
        pytest -v
        ;;
esac

echo ""
echo "✅ Тестирование завершено!"

