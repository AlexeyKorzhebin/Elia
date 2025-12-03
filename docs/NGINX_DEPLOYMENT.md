# Настройка Nginx для Elia Platform

## Почему Nginx не в Dockerfile?

**Nginx должен быть установлен на хосте, а не внутри Docker контейнера**, потому что:

1. **Reverse Proxy на хосте**: Nginx работает как reverse proxy между интернетом и Docker контейнером
2. **SSL/TLS терминация**: Nginx обрабатывает HTTPS соединения и проксирует HTTP запросы к контейнеру
3. **Порты**: Nginx слушает порты 80 и 443 на хосте, контейнер работает на localhost:8000
4. **Производительность**: Разделение ответственности улучшает производительность и безопасность

## Автоматическая настройка

Скрипт `deploy-ubuntu.sh` автоматически настраивает Nginx при развёртывании:

```bash
./scripts/deploy-ubuntu.sh -d elia.su -k sk-... -e admin@elia.su
```

### Что делает скрипт:

1. **Устанавливает Nginx и Certbot** (если не указан `--no-nginx`)
2. **Создаёт конфигурацию** `/etc/nginx/sites-available/elia-platform`
3. **Настраивает проксирование** на `http://127.0.0.1:8000`
4. **Получает SSL сертификат** от Let's Encrypt (если указан email)
5. **Настраивает автоматическое обновление** сертификата

## Конфигурация Nginx

### Базовая конфигурация (HTTP)

```nginx
server {
    server_name elia.su;
    
    access_log /var/log/nginx/elia-access.log;
    error_log /var/log/nginx/elia-error.log;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    listen 80;
}
```

### Конфигурация с SSL (HTTPS)

После получения SSL сертификата Certbot автоматически обновляет конфигурацию:

```nginx
server {
    server_name elia.su;
    
    # ... (те же настройки) ...
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        # ... (те же заголовки) ...
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/elia.su/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/elia.su/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = elia.su) {
        return 301 https://$host$request_uri;
    }
    
    listen 80;
    server_name elia.su;
    return 404;
}
```

## Docker Compose конфигурация

Контейнер должен слушать только на localhost:8000:

```yaml
services:
  elia-app:
    image: alekseykorzhebin/elia-platform:latest
    container_name: elia-platform
    ports:
      - "127.0.0.1:8000:80"  # Только локальный доступ
    # ... остальная конфигурация ...
```

**Важно:** Порт должен быть `127.0.0.1:8000:80`, а не `80:80`, чтобы контейнер был доступен только через Nginx.

## Ручная настройка

Если нужно настроить Nginx вручную:

```bash
# 1. Установка
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 2. Создание конфигурации
sudo nano /etc/nginx/sites-available/elia-platform
# (вставить конфигурацию выше)

# 3. Активация
sudo ln -s /etc/nginx/sites-available/elia-platform /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 4. Проверка и запуск
sudo nginx -t
sudo systemctl restart nginx

# 5. Получение SSL сертификата
sudo certbot --nginx -d elia.su --email admin@elia.su --agree-tos --non-interactive --redirect
```

## Обновление конфигурации

Скрипт `update-server.sh` автоматически проверяет и обновляет конфигурацию Nginx при обновлении приложения.

## Проверка работы

```bash
# Проверка контейнера
curl http://127.0.0.1:8000/health

# Проверка через Nginx (HTTP)
curl http://elia.su/health

# Проверка через Nginx (HTTPS)
curl https://elia.su/health

# Проверка статуса Nginx
sudo systemctl status nginx

# Проверка конфигурации
sudo nginx -t

# Просмотр логов
sudo tail -f /var/log/nginx/elia-access.log
sudo tail -f /var/log/nginx/elia-error.log
```

## Устранение проблем

### Проблема: 502 Bad Gateway

**Причина:** Nginx не может подключиться к контейнеру

**Решение:**
1. Проверьте, что контейнер запущен: `docker ps`
2. Проверьте порт: `curl http://127.0.0.1:8000/health`
3. Проверьте конфигурацию Nginx: `sudo nginx -t`

### Проблема: Статические файлы не загружаются

**Причина:** Nginx пытается раздавать статику напрямую, но файлов нет на хосте

**Решение:** Убедитесь, что в конфигурации Nginx нет алиасов для `/static/`. Все запросы должны проксироваться к контейнеру.

### Проблема: SSL сертификат не обновляется

**Причина:** Certbot timer не настроен

**Решение:**
```bash
sudo systemctl status certbot.timer
sudo systemctl enable certbot.timer
sudo certbot renew --dry-run
```

## Безопасность

1. **Firewall:** Откройте только необходимые порты:
   ```bash
   sudo ufw allow 22/tcp  # SSH
   sudo ufw allow 80/tcp  # HTTP
   sudo ufw allow 443/tcp # HTTPS
   ```

2. **Контейнер:** Доступен только на localhost, не на внешнем интерфейсе

3. **SSL:** Используйте Let's Encrypt для автоматического обновления сертификатов

## Дополнительные ресурсы

- [Документация Nginx](https://nginx.org/ru/docs/)
- [Certbot документация](https://certbot.eff.org/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**Вернуться к [оглавлению документации](README.md)**

