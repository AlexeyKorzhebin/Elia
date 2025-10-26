#!/bin/bash
# Скрипт для перезапуска приложения на сервере

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVER="root@43.245.224.114"

echo -e "${BLUE}=== Перезапуск Elia Platform ===${NC}"
echo ""

echo -e "${BLUE}[1/3]${NC} Остановка контейнера..."
ssh $SERVER "cd /opt/elia-platform && docker compose down"
echo -e "${GREEN}✓ Остановлен${NC}"
echo ""

echo -e "${BLUE}[2/3]${NC} Запуск контейнера..."
ssh $SERVER "cd /opt/elia-platform && docker compose up -d"
echo -e "${GREEN}✓ Запущен${NC}"
echo ""

echo -e "${BLUE}[3/3]${NC} Проверка работоспособности..."
sleep 5

if ssh $SERVER "curl -sf http://localhost/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Приложение работает${NC}"
    echo ""
    ssh $SERVER "cd /opt/elia-platform && docker compose ps"
else
    echo -e "${RED}✗ Приложение не отвечает${NC}"
    exit 1
fi

