# 🐧 Развертывание Elia Platform на Ubuntu сервере - Итоговая инструкция

## ✅ Что было создано для Ubuntu развертывания

1. ✅ **Полное руководство** - `UBUNTU_DEPLOYMENT.md`
2. ✅ **Автоматический скрипт** - `scripts/deploy-ubuntu.sh`
3. ✅ **Продакшн конфигурация** - `env.production.example`
4. ✅ **Шпаргалка команд** - `ubuntu-cheatsheet.txt`
5. ✅ **Настройка Nginx** reverse proxy
6. ✅ **Настройка SSL** с Let's Encrypt
7. ✅ **Systemd сервис** для автозапуска
8. ✅ **Автоматические бэкапы**
9. ✅ **Настройка файрвола**

---

## 🚀 3 способа развертывания на Ubuntu

### Способ 1: Автоматический (рекомендуется) ⚡

```bash
# На Ubuntu сервере выполните:
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git unzip

# Скачайте и запустите скрипт
wget https://raw.githubusercontent.com/ваш-репозиторий/main/scripts/deploy-ubuntu.sh
chmod +x deploy-ubuntu.sh
./deploy-ubuntu.sh -d example.com -k sk-ваш-ключ -e admin@example.com
```

**Что делает скрипт:**
- ✅ Устанавливает Docker и Docker Compose
- ✅ Создает структуру проекта в `/opt/elia-platform`
- ✅ Настраивает `.env` конфигурацию
- ✅ Устанавливает и настраивает Nginx
- ✅ Получает SSL сертификат
- ✅ Создает systemd сервис
- ✅ Настраивает файрвол
- ✅ Создает скрипт бэкапа
- ✅ Запускает приложение

### Способ 2: Полуавтоматический 📝

```bash
# 1. Установите Docker (см. UBUNTU_DEPLOYMENT.md)
# 2. Скопируйте файлы проекта на сервер
# 3. Создайте .env из env.production.example
# 4. Запустите:
docker compose build
docker compose up -d
```

### Способ 3: Ручной 🔧

Следуйте пошаговой инструкции в `UBUNTU_DEPLOYMENT.md`

---

## 📋 Требования к серверу

- **ОС:** Ubuntu 20.04+ (рекомендуется 22.04 LTS)
- **RAM:** минимум 2GB (рекомендуется 4GB+)
- **Диск:** минимум 10GB свободного места
- **CPU:** минимум 1 ядро
- **Сеть:** открытые порты 80, 443
- **Домен:** настроенный DNS на IP сервера

---

## 🗄️ Использование текущей БД на Ubuntu сервере

### Как это работает:

База данных монтируется через Docker volume:
```yaml
volumes:
  - ./data:/app/data  # БД хранится в /opt/elia-platform/data/
```

**На сервере:**
- ✅ БД находится в `/opt/elia-platform/data/elia.db`
- ✅ Все изменения сохраняются ВНЕ контейнера
- ✅ При перезапуске сервера данные НЕ теряются
- ✅ При обновлении приложения данные НЕ удаляются

### Практические действия:

```bash
# Если у вас есть БД на локальной машине:
# 1. Скопируйте БД на сервер
scp elia.db user@server:/tmp/

# 2. На сервере переместите БД
sudo mkdir -p /opt/elia-platform/data
sudo mv /tmp/elia.db /opt/elia-platform/data/
sudo chown $USER:$USER /opt/elia-platform/data/elia.db

# 3. Запустите приложение
sudo systemctl start elia-platform
```

### Бэкап и восстановление на сервере:

```bash
# Автоматический бэкап (настроен скриптом)
/opt/elia-platform/backup.sh

# Ручной бэкап
sudo cp /opt/elia-platform/data/elia.db /opt/backups/elia-platform/elia_$(date +%Y%m%d).db

# Восстановление
sudo systemctl stop elia-platform
sudo cp /opt/backups/elia-platform/elia_YYYYMMDD.db /opt/elia-platform/data/elia.db
sudo systemctl start elia-platform
```

---

## ⚙️ Изменение параметров через .env на сервере

### Как это работает:

Файл `.env` находится на сервере в `/opt/elia-platform/.env` и монтируется в контейнер.

### Изменить любой параметр:

```bash
# 1. Отредактируйте .env на сервере
sudo nano /opt/elia-platform/.env

# 2. Перезапустите сервис
sudo systemctl restart elia-platform
```

**База данных и файлы НЕ пострадают!**

### Примеры изменений:

```bash
# Изменить порт:
echo "PORT=9000" | sudo tee -a /opt/elia-platform/.env
sudo systemctl restart elia-platform

# Включить debug:
echo "DEBUG=true" | sudo tee -a /opt/elia-platform/.env
echo "LOG_LEVEL=DEBUG" | sudo tee -a /opt/elia-platform/.env
sudo systemctl restart elia-platform

# Сменить OpenAI ключ:
sudo nano /opt/elia-platform/.env  # Отредактируйте OPENAI_API_KEY
sudo systemctl restart elia-platform
```

---

## 🌐 Настройка домена и SSL

### Автоматическая настройка (через скрипт):

```bash
./deploy-ubuntu.sh -d example.com -k sk-... -e admin@example.com
```

### Ручная настройка:

```bash
# 1. Настройте DNS: A запись example.com → IP сервера

# 2. Установите Nginx
sudo apt install -y nginx

# 3. Создайте конфигурацию (см. UBUNTU_DEPLOYMENT.md)

# 4. Получите SSL сертификат
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com
```

---

## 📊 Структура файлов на сервере

```
/opt/elia-platform/                    # Основная директория
├── .env                               # Конфигурация приложения
├── docker-compose.yml                 # Docker Compose
├── Dockerfile                         # Docker образ
├── app/                               # Код приложения
├── static/                            # Статические файлы
├── templates/                          # HTML шаблоны
├── data/                              # База данных (персистентно)
│   └── elia.db
├── logs/                              # Логи приложения (персистентно)
├── static/uploads/                     # Загруженные файлы (персистентно)
└── backup.sh                          # Скрипт бэкапа

/etc/nginx/sites-available/elia-platform    # Конфигурация Nginx
/etc/systemd/system/elia-platform.service   # Systemd сервис
/opt/backups/elia-platform/                 # Автоматические бэкапы
```

**Все данные персистентны** - хранятся вне контейнера!

---

## 🔧 Управление на сервере

### Основные команды:

```bash
# Статус сервисов
sudo systemctl status elia-platform
sudo systemctl status nginx
sudo systemctl status docker

# Управление приложением
sudo systemctl start elia-platform
sudo systemctl stop elia-platform
sudo systemctl restart elia-platform

# Логи
sudo journalctl -u elia-platform -f
docker compose logs -f
sudo tail -f /var/log/nginx/elia-access.log

# Мониторинг ресурсов
docker stats
htop
df -h
```

### Обновление приложения:

```bash
cd /opt/elia-platform

# Остановите сервис
sudo systemctl stop elia-platform

# Обновите код
git pull

# Пересоберите образ
docker compose build

# Запустите сервис
sudo systemctl start elia-platform

# Данные останутся на месте!
```

---

## 🛡️ Безопасность

### Что настроено автоматически:

- ✅ **Файрвол UFW** - открыты только порты 22, 80, 443
- ✅ **SSL сертификаты** - автоматическое обновление
- ✅ **Автообновления системы** - безопасность
- ✅ **Изоляция контейнера** - приложение в Docker
- ✅ **Правильные права доступа** - файлы принадлежат пользователю

### Дополнительные меры:

```bash
# Смена SSH порта (опционально)
sudo nano /etc/ssh/sshd_config
# Измените: Port 2222
sudo systemctl restart ssh

# Отключение root логина
sudo nano /etc/ssh/sshd_config
# Измените: PermitRootLogin no
sudo systemctl restart ssh

# Настройка fail2ban (защита от брутфорса)
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📈 Мониторинг и алерты

### Настройка мониторинга:

```bash
# Установка htop для мониторинга
sudo apt install -y htop

# Создание скрипта мониторинга
sudo nano /opt/elia-platform/monitor.sh
```

Содержимое скрипта мониторинга:

```bash
#!/bin/bash
# Проверка статуса Elia Platform

if ! sudo systemctl is-active --quiet elia-platform; then
    echo "ALERT: Elia Platform is down!" | mail -s "Elia Platform Alert" admin@example.com
fi

if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "ALERT: Health check failed!" | mail -s "Elia Platform Alert" admin@example.com
fi

# Проверка диска
DISK_USAGE=$(df /opt/elia-platform | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERT: Disk usage is ${DISK_USAGE}%" | mail -s "Disk Alert" admin@example.com
fi
```

```bash
# Сделайте исполняемым
sudo chmod +x /opt/elia-platform/monitor.sh

# Добавьте в crontab (проверка каждые 5 минут)
sudo crontab -e
# Добавьте: */5 * * * * /opt/elia-platform/monitor.sh
```

---

## 🐛 Устранение неполадок

### Проблема: Контейнер не запускается

```bash
# Проверьте логи
sudo journalctl -u elia-platform -f
docker compose logs

# Проверьте конфигурацию
docker compose config

# Проверьте права доступа
sudo chown -R $USER:$USER /opt/elia-platform
```

### Проблема: Nginx не проксирует

```bash
# Проверьте конфигурацию
sudo nginx -t

# Проверьте статус
sudo systemctl status nginx

# Проверьте, что приложение слушает порт 8000
sudo netstat -tlnp | grep 8000
```

### Проблема: SSL не работает

```bash
# Проверьте сертификат
sudo certbot certificates

# Обновите сертификат
sudo certbot renew --dry-run

# Проверьте конфигурацию Nginx
sudo nginx -t
```

### Проблема: Нет доступа к сайту

```bash
# Проверьте файрвол
sudo ufw status

# Проверьте DNS
nslookup example.com

# Проверьте порты
sudo netstat -tlnp | grep -E ":(80|443|8000)"
```

---

## ✅ Проверка работоспособности

После развертывания проверьте:

```bash
# 1. Статус всех сервисов
sudo systemctl status elia-platform nginx docker

# 2. Health check приложения
curl http://example.com/health
# Ожидается: {"status":"healthy"}

# 3. Доступность сайта
curl -I http://example.com
curl -I https://example.com

# 4. SSL сертификат
curl -I https://example.com
# Должен показать статус 200

# 5. Логи без ошибок
sudo journalctl -u elia-platform --since "1 hour ago" | grep -i error
```

---

## 📚 Документация

Файл | Описание
-----|----------
`UBUNTU_DEPLOYMENT.md` | Полное руководство по развертыванию
`scripts/deploy-ubuntu.sh` | Автоматический скрипт развертывания
`env.production.example` | Пример продакшн конфигурации
`ubuntu-cheatsheet.txt` | Шпаргалка команд для Ubuntu

---

## 🎯 Итоговая проверка

После развертывания у вас должно быть:

1. ✅ **Docker** установлен и работает
2. ✅ **Elia Platform** запущен и отвечает на health check
3. ✅ **Nginx** настроен и проксирует запросы
4. ✅ **SSL сертификат** получен и работает
5. ✅ **Systemd сервис** настроен для автозапуска
6. ✅ **Файрвол** настроен и защищает сервер
7. ✅ **Автоматические бэкапы** настроены
8. ✅ **Домен** доступен по HTTPS

---

## 🚀 Готово к использованию!

**Ваш Elia Platform развернут на Ubuntu сервере!**

- 🌐 **Сайт:** https://example.com
- 🔍 **Health check:** https://example.com/health
- 📊 **Мониторинг:** `sudo systemctl status elia-platform`
- 🔄 **Обновление:** `git pull && docker compose build && sudo systemctl restart elia-platform`
- 💾 **Бэкап:** `/opt/elia-platform/backup.sh`

**Все данные персистентны и безопасны! 🛡️**

