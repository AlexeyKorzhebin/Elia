#!/bin/bash
# Скрипт для проверки статуса сервера и приложения

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SERVER="root@43.245.224.114"

echo -e "${BLUE}=== Статус Elia Platform ===${NC}"
echo ""

# Информация о сервере
echo -e "${BLUE}Сервер:${NC}"
ssh $SERVER "hostname && uptime"
echo ""

# Статус Docker контейнера
echo -e "${BLUE}Docker контейнер:${NC}"
ssh $SERVER "cd /opt/elia-platform && docker compose ps"
echo ""

# Здоровье приложения
echo -e "${BLUE}Здоровье приложения:${NC}"
HEALTH=$(ssh $SERVER "curl -sf http://localhost/health" 2>/dev/null || echo '{"status":"error"}')
echo $HEALTH | python3 -m json.tool
echo ""

# Использование ресурсов
echo -e "${BLUE}Использование ресурсов:${NC}"
ssh $SERVER "docker stats elia-platform --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'"
echo ""

# Размер базы данных
echo -e "${BLUE}База данных:${NC}"
ssh $SERVER "ls -lh /opt/elia-platform/elia.db 2>/dev/null || echo 'База данных не найдена'"
echo ""

# Логи (последние 10 строк)
echo -e "${BLUE}Последние логи:${NC}"
ssh $SERVER "docker logs elia-platform --tail=10"

