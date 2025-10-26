# 🐧 Развертывание Elia Platform на Ubuntu сервере

## 📋 Требования к серверу

- **ОС:** Ubuntu 20.04+ (рекомендуется 22.04 LTS)
- **RAM:** минимум 2GB (рекомендуется 4GB+)
- **Диск:** минимум 10GB свободного места
- **CPU:** минимум 1 ядро
- **Сеть:** открытые порты 80, 443 (для веб-доступа)

## 🚀 Быстрая установка (автоматический скрипт)

### Шаг 1: Подготовка сервера

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите необходимые пакеты
sudo apt install -y curl wget git unzip
```

### Шаг 2: Загрузите и запустите скрипт установки

```bash
# Скачайте скрипт установки
wget https://raw.githubusercontent.com/ваш-репозиторий/main/scripts/deploy-ubuntu.sh

# Сделайте исполняемым
chmod +x deploy-ubuntu.sh

# Запустите установку
./deploy-ubuntu.sh
```

## 🔧 Ручная установка (пошагово)

### Шаг 1: Установка Docker

```bash
# Удалите старые версии Docker
sudo apt remove -y docker docker-engine docker.io containerd runc

# Установите зависимости
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Добавьте официальный GPG ключ Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Добавьте репозиторий Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установите Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER

# Включите автозапуск Docker
sudo systemctl enable docker
sudo systemctl start docker

# Перелогиньтесь или выполните
newgrp docker
```

### Шаг 2: Установка Docker Compose

```bash
# Проверьте версию Docker Compose
docker compose version

# Если не установлен, установите отдельно
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Шаг 3: Подготовка проекта

```bash
# Создайте директорию для проекта
sudo mkdir -p /opt/elia-platform
cd /opt/elia-platform

# Клонируйте репозиторий (замените на ваш URL)
git clone https://github.com/ваш-пользователь/ваш-репозиторий.git .

# Или загрузите архив проекта
# wget https://github.com/ваш-пользователь/ваш-репозиторий/archive/main.zip
# unzip main.zip
# mv ваш-репозиторий-main/* .
```

### Шаг 4: Настройка конфигурации

```bash
# Создайте .env файл для продакшн
sudo nano .env
```

Содержимое `.env` для продакшн:

```env
# База данных
DATABASE_URL=sqlite+aiosqlite:///./data/elia.db

# Сервер
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Загрузка файлов
UPLOAD_DIR=static/uploads
MAX_UPLOAD_SIZE=52428800

# Приложение
APP_NAME=Elia AI Platform
VERSION=1.0.0

# Логирование
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_RETENTION_DAYS=30

# OpenAI API (ОБЯЗАТЕЛЬНО замените!)
OPENAI_API_KEY=ваш-реальный-ключ-openai
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# Дополнительные настройки для продакшн
PYTHONPATH=/app
PYTHONUNBUFFERED=1
```

### Шаг 5: Создание необходимых директорий

```bash
# Создайте директории с правильными правами
sudo mkdir -p data logs static/uploads
sudo chown -R $USER:$USER data logs static/uploads
sudo chmod -R 755 data logs static/uploads
```

### Шаг 6: Сборка и запуск

```bash
# Соберите Docker образ
docker compose build

# Запустите в фоне
docker compose up -d

# Проверьте статус
docker compose ps
```

## 🌐 Настройка Nginx (рекомендуется)

### Установка Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Создание конфигурации

```bash
sudo nano /etc/nginx/sites-available/elia-platform
```

Содержимое конфигурации:

```nginx
server {
    listen 80;
    server_name ваш-домен.com;  # Замените на ваш домен или IP

    # Логи
    access_log /var/log/nginx/elia-access.log;
    error_log /var/log/nginx/elia-error.log;

    # Максимальный размер загружаемых файлов
    client_max_body_size 50M;

    # Проксирование на Docker контейнер
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Статические файлы
    location /static/ {
        alias /opt/elia-platform/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Загруженные файлы
    location /uploads/ {
        alias /opt/elia-platform/static/uploads/;
        expires 1d;
    }
}
```

### Активация конфигурации

```bash
# Создайте символическую ссылку
sudo ln -s /etc/nginx/sites-available/elia-platform /etc/nginx/sites-enabled/

# Удалите дефолтную конфигурацию
sudo rm /etc/nginx/sites-enabled/default

# Проверьте конфигурацию
sudo nginx -t

# Перезапустите Nginx
sudo systemctl restart nginx
```

## 🔒 Настройка SSL с Let's Encrypt

### Установка Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Получение сертификата

```bash
# Замените на ваш домен
sudo certbot --nginx -d ваш-домен.com

# Автоматическое обновление
sudo crontab -e
# Добавьте строку:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔄 Настройка автозапуска (Systemd)

### Создание systemd сервиса

```bash
sudo nano /etc/systemd/system/elia-platform.service
```

Содержимое сервиса:

```ini
[Unit]
Description=Elia AI Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/elia-platform
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
ExecReload=/usr/bin/docker compose restart
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

### Активация сервиса

```bash
# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable elia-platform

# Запустите сервис
sudo systemctl start elia-platform

# Проверьте статус
sudo systemctl status elia-platform
```

## 📊 Мониторинг и логи

### Просмотр логов

```bash
# Логи приложения
docker compose logs -f

# Логи Nginx
sudo tail -f /var/log/nginx/elia-access.log
sudo tail -f /var/log/nginx/elia-error.log

# Логи systemd
sudo journalctl -u elia-platform -f
```

### Мониторинг ресурсов

```bash
# Использование Docker
docker stats

# Использование диска
df -h

# Использование памяти
free -h

# Процессы
htop
```

## 🔧 Обслуживание

### Обновление приложения

```bash
cd /opt/elia-platform

# Остановите сервис
sudo systemctl stop elia-platform

# Получите новый код
git pull

# Пересоберите образ
docker compose build

# Запустите сервис
sudo systemctl start elia-platform
```

### Бэкап данных

```bash
# Создайте скрипт бэкапа
sudo nano /opt/elia-platform/backup.sh
```

Содержимое скрипта:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/elia-platform"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап базы данных
cp /opt/elia-platform/data/elia.db $BACKUP_DIR/elia_$DATE.db

# Бэкап загруженных файлов
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /opt/elia-platform static/uploads/

# Бэкап конфигурации
cp /opt/elia-platform/.env $BACKUP_DIR/env_$DATE

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "env_*" -mtime +30 -delete

echo "Бэкап завершен: $DATE"
```

```bash
# Сделайте скрипт исполняемым
sudo chmod +x /opt/elia-platform/backup.sh

# Добавьте в crontab для ежедневного бэкапа
sudo crontab -e
# Добавьте строку:
# 0 2 * * * /opt/elia-platform/backup.sh
```

### Восстановление из бэкапа

```bash
# Остановите сервис
sudo systemctl stop elia-platform

# Восстановите БД
cp /opt/backups/elia-platform/elia_YYYYMMDD_HHMMSS.db /opt/elia-platform/data/elia.db

# Восстановите файлы
tar -xzf /opt/backups/elia-platform/uploads_YYYYMMDD_HHMMSS.tar.gz -C /opt/elia-platform/

# Запустите сервис
sudo systemctl start elia-platform
```

## 🛡️ Безопасность

### Настройка файрвола

```bash
# Установите UFW
sudo apt install -y ufw

# Настройте правила
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Включите файрвол
sudo ufw enable
```

### Обновление системы

```bash
# Автоматические обновления безопасности
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 🐛 Устранение неполадок

### Проблема: Контейнер не запускается

```bash
# Проверьте логи
docker compose logs

# Проверьте статус
docker compose ps

# Проверьте конфигурацию
docker compose config
```

### Проблема: Nginx не проксирует

```bash
# Проверьте конфигурацию Nginx
sudo nginx -t

# Проверьте статус Nginx
sudo systemctl status nginx

# Проверьте, что приложение слушает порт 8000
sudo netstat -tlnp | grep 8000
```

### Проблема: Нет доступа к сайту

```bash
# Проверьте файрвол
sudo ufw status

# Проверьте, что порты открыты
sudo netstat -tlnp | grep -E ":(80|443|8000)"
```

## 📈 Оптимизация производительности

### Настройка Docker

```bash
# Ограничьте ресурсы контейнера в docker-compose.yml
```

Добавьте в `docker-compose.yml`:

```yaml
services:
  elia-app:
    # ... существующая конфигурация ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Настройка Nginx

```bash
sudo nano /etc/nginx/nginx.conf
```

Добавьте в секцию `http`:

```nginx
# Кэширование
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=elia_cache:10m max_size=1g inactive=60m;

# Сжатие
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

## ✅ Проверка работоспособности

```bash
# Проверьте статус всех сервисов
sudo systemctl status elia-platform
sudo systemctl status nginx
sudo systemctl status docker

# Проверьте доступность сайта
curl -I http://ваш-домен.com
curl -I https://ваш-домен.com

# Проверьте health check
curl http://ваш-домен.com/health
```

## 📚 Полезные команды

```bash
# Управление сервисом
sudo systemctl start elia-platform
sudo systemctl stop elia-platform
sudo systemctl restart elia-platform
sudo systemctl status elia-platform

# Управление Docker
docker compose up -d
docker compose down
docker compose restart
docker compose logs -f

# Управление Nginx
sudo systemctl restart nginx
sudo nginx -t
sudo systemctl reload nginx

# Мониторинг
docker stats
sudo htop
df -h
```

## 🎯 Итоговая проверка

После установки проверьте:

1. ✅ Docker работает: `docker --version`
2. ✅ Приложение запущено: `sudo systemctl status elia-platform`
3. ✅ Nginx работает: `sudo systemctl status nginx`
4. ✅ Сайт доступен: `curl http://ваш-домен.com`
5. ✅ SSL работает: `curl https://ваш-домен.com`
6. ✅ Health check: `curl http://ваш-домен.com/health`

---

**Готово! Ваш Elia Platform развернут на Ubuntu сервере! 🚀**

