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

# Проверка и обновление конфигурации Nginx (если нужно)
echo ""
echo -e "${BLUE}[5/7]${NC} Проверка конфигурации Nginx..."
if ssh $SERVER "systemctl is-active --quiet nginx 2>/dev/null"; then
    echo -e "${GREEN}✓ Nginx запущен${NC}"
    
    # Проверяем, что Nginx проксирует на правильный порт
    if ssh $SERVER "grep -q 'proxy_pass http://127.0.0.1:8000' /etc/nginx/sites-enabled/elia-platform 2>/dev/null"; then
        echo -e "${GREEN}✓ Конфигурация Nginx корректна${NC}"
    else
        echo -e "${YELLOW}⚠ Обновление конфигурации Nginx...${NC}"
        ssh $SERVER "cat > /tmp/nginx-update.conf << 'NGINXEOF'
server {
    server_name elia.su;
    
    access_log /var/log/nginx/elia-access.log;
    error_log /var/log/nginx/elia-error.log;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/elia.su/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/elia.su/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if (\$host = elia.su) {
        return 301 https://\$host\$request_uri;
    }
    
    listen 80;
    server_name elia.su;
    return 404;
}
NGINXEOF
sudo cp /tmp/nginx-update.conf /etc/nginx/sites-available/elia-platform
sudo nginx -t && sudo systemctl reload nginx"
        echo -e "${GREEN}✓ Конфигурация Nginx обновлена${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Nginx не запущен (пропускаем проверку)${NC}"
fi

# Проверка работоспособности
echo ""
echo -e "${BLUE}[6/7]${NC} Проверка работоспособности..."
sleep 5  # Даем время на запуск

if ssh $SERVER "curl -sf http://127.0.0.1:8000/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Приложение работает${NC}"
else
    echo -e "${RED}✗ Приложение не отвечает на порту 8000${NC}"
    echo ""
    echo "Последние логи:"
    ssh $SERVER "docker logs elia-platform --tail=20"
    exit 1
fi

# Проверка через Nginx (если установлен)
echo ""
echo -e "${BLUE}[7/7]${NC} Проверка через Nginx..."
if ssh $SERVER "systemctl is-active --quiet nginx 2>/dev/null"; then
    if ssh $SERVER "curl -sfk https://elia.su/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Приложение доступно через HTTPS${NC}"
    elif ssh $SERVER "curl -sf http://elia.su/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Приложение доступно через HTTP${NC}"
    else
        echo -e "${YELLOW}⚠ Приложение не доступно через домен (проверьте DNS и Nginx)${NC}"
    fi
fi

echo ""
echo -e "${GREEN}=== Обновление завершено успешно! ===${NC}"
echo ""
echo "Статус контейнера:"
ssh $SERVER "cd $APP_DIR && docker compose ps"
echo ""
echo -e "${BLUE}Приложение доступно:${NC}"
echo "  - Локально: http://127.0.0.1:8000/health"
if ssh $SERVER "systemctl is-active --quiet nginx 2>/dev/null"; then
    echo "  - Через домен: https://elia.su"
fi

