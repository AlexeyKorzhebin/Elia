#!/bin/bash
# Скрипт автоматической настройки Docker окружения для Elia Platform

set -e

echo "🚀 Настройка Docker окружения для Elia Platform..."
echo ""

# Создание необходимых директорий
echo "📁 Создание директорий..."
mkdir -p data logs static/uploads

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cat > .env << 'EOF'
# Конфигурация базы данных
DATABASE_URL=sqlite+aiosqlite:///./data/elia.db

# Настройки сервера
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Настройки загрузки файлов
UPLOAD_DIR=static/uploads
MAX_UPLOAD_SIZE=52428800

# Настройки приложения
APP_NAME=Elia AI Platform
VERSION=1.0.0

# Настройки логирования
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_RETENTION_DAYS=30

# OpenAI API (замените на ваш ключ!)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
EOF
    echo "✅ Файл .env создан"
    echo "⚠️  ВАЖНО: Отредактируйте .env и добавьте ваш OPENAI_API_KEY"
else
    echo "✅ Файл .env уже существует"
fi

# Проверка существующей БД
if [ -f elia.db ]; then
    echo ""
    read -p "❓ Найдена существующая БД (elia.db). Переместить в data/? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mv elia.db data/
        echo "✅ БД перемещена в data/elia.db"
    fi
fi

echo ""
echo "✅ Настройка завершена!"
echo ""
echo "Теперь выполните:"
echo "  docker-compose build"
echo "  docker-compose up -d"
echo ""
echo "Проверьте работу:"
echo "  curl http://localhost:8000/health"
echo ""
echo "Подробная документация:"
echo "  - DOCKER_QUICKSTART.md (быстрый старт)"
echo "  - DOCKER_GUIDE.md (полное руководство)"
echo ""

