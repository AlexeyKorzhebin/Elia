#!/bin/bash
# Скрипт обновления Elia Platform на удаленном сервере
# Использует SSH ключи для беспарольного доступа

set -e  # Остановить при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVER="root@43.245.224.114"
APP_DIR="/opt/elia-platform"

echo -e "${BLUE}=== Обновление Elia Platform на сервере ===${NC}"
echo ""

# Проверка SSH подключения
echo -e "${BLUE}[1/5]${NC} Проверка подключения к серверу..."
if ssh -o BatchMode=yes -o ConnectTimeout=5 $SERVER "echo 'OK'" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Подключение установлено${NC}"
else
    echo -e "${RED}✗ Не удалось подключиться к серверу${NC}"
    exit 1
fi

# Загрузка нового образа
echo ""
echo -e "${BLUE}[2/5]${NC} Загрузка нового Docker образа..."
ssh $SERVER "cd $APP_DIR && docker compose pull"
echo -e "${GREEN}✓ Образ загружен${NC}"

# Остановка старого контейнера
echo ""
echo -e "${BLUE}[3/5]${NC} Остановка текущего контейнера..."
ssh $SERVER "cd $APP_DIR && docker compose down"
echo -e "${GREEN}✓ Контейнер остановлен${NC}"

# Запуск нового контейнера
echo ""
echo -e "${BLUE}[4/5]${NC} Запуск обновленного контейнера..."
ssh $SERVER "cd $APP_DIR && docker compose up -d"
echo -e "${GREEN}✓ Контейнер запущен${NC}"

# Проверка работоспособности
echo ""
echo -e "${BLUE}[5/5]${NC} Проверка работоспособности..."
sleep 5  # Даем время на запуск

if ssh $SERVER "curl -sf http://localhost/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Приложение работает${NC}"
    echo ""
    echo -e "${GREEN}=== Обновление завершено успешно! ===${NC}"
    echo ""
    echo "Статус контейнера:"
    ssh $SERVER "cd $APP_DIR && docker compose ps"
    echo ""
    echo -e "${BLUE}Приложение доступно по адресу:${NC} http://43.245.224.114"
else
    echo -e "${RED}✗ Приложение не отвечает${NC}"
    echo ""
    echo "Последние логи:"
    ssh $SERVER "docker logs elia-platform --tail=20"
    exit 1
fi

