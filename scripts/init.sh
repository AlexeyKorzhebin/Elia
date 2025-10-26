#!/bin/bash
# Скрипт инициализации проекта

set -e

echo "🚀 Инициализация Elia AI Platform..."

# Проверка Python версии
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Требуется Python $required_version или выше. Установлена версия: $python_version"
    exit 1
fi

echo "✅ Python версия: $python_version"

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "🔄 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание .env файла
if [ ! -f ".env" ]; then
    echo "⚙️  Создание .env файла..."
    cp .env.example .env
    echo "✅ Создан .env файл. Отредактируйте его при необходимости."
fi

# Создание директорий
echo "📁 Создание необходимых директорий..."
mkdir -p static/uploads
mkdir -p data

# Загрузка тестовых данных
echo "📊 Загрузка тестовых данных..."
python -m app.fixtures

echo ""
echo "✅ Инициализация завершена!"
echo ""
echo "Для запуска приложения выполните:"
echo "  source venv/bin/activate"
echo "  python -m uvicorn app.main:app --reload"
echo ""
echo "Или запустите через Docker:"
echo "  docker-compose up -d"
echo ""
echo "Приложение будет доступно по адресу: http://localhost:8000"

