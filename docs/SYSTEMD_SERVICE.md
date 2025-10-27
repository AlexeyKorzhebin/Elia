# Systemd сервис для Elia Platform

Elia Platform настроен как systemd сервис для автоматического запуска и управления.

---

## ✅ Преимущества systemd

- 🚀 **Автозапуск** при перезагрузке сервера
- 🔄 **Автоматический перезапуск** при сбоях
- 📊 **Централизованное логирование** через journald
- 🎛️ **Удобное управление** через systemctl
- ⚡ **Быстрый старт** после загрузки системы

---

## 📋 Управление сервисом

### Базовые команды

```bash
# Запустить сервис
sudo systemctl start elia-platform

# Остановить сервис
sudo systemctl stop elia-platform

# Перезапустить сервис
sudo systemctl restart elia-platform

# Перезагрузить конфигурацию
sudo systemctl reload elia-platform

# Проверить статус
sudo systemctl status elia-platform
```

### Автозапуск

```bash
# Включить автозапуск (уже включен)
sudo systemctl enable elia-platform

# Отключить автозапуск
sudo systemctl disable elia-platform

# Проверить включен ли автозапуск
sudo systemctl is-enabled elia-platform
```

---

## 📊 Мониторинг и логи

### Просмотр логов

```bash
# Последние логи
sudo journalctl -u elia-platform

# Логи в реальном времени
sudo journalctl -u elia-platform -f

# Последние 100 строк
sudo journalctl -u elia-platform -n 100

# Логи за сегодня
sudo journalctl -u elia-platform --since today

# Логи за последний час
sudo journalctl -u elia-platform --since "1 hour ago"
```

### Статус и информация

```bash
# Полный статус
systemctl status elia-platform -l

# Только активность
systemctl is-active elia-platform

# Проверка ошибок
systemctl is-failed elia-platform

# Показать конфигурацию
systemctl cat elia-platform
```

---

## 🔧 Конфигурация сервиса

### Расположение файла

```
/etc/systemd/system/elia-platform.service
```

### Содержимое

```ini
[Unit]
Description=Elia AI Platform - Medical Practice Management System
Documentation=https://github.com/AlexeyKorzhebin/Elia
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/elia-platform
ExecStartPre=/usr/bin/docker compose pull --quiet
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
ExecReload=/usr/bin/docker compose restart
TimeoutStartSec=0
Restart=on-failure
RestartSec=10s

# Security settings
PrivateTmp=yes
NoNewPrivileges=yes

# User and group
User=root
Group=root

# Environment
Environment="COMPOSE_PROJECT_NAME=elia-platform"

[Install]
WantedBy=multi-user.target
```

### Описание параметров

| Параметр | Описание |
|----------|----------|
| `Type=oneshot` | Сервис запускается один раз |
| `RemainAfterExit=yes` | Считается активным после завершения запуска |
| `WorkingDirectory` | Рабочая директория с docker-compose.yml |
| `ExecStartPre` | Обновление образа перед запуском |
| `ExecStart` | Команда запуска (docker compose up) |
| `ExecStop` | Команда остановки (docker compose down) |
| `Restart=on-failure` | Автоперезапуск при сбое |
| `RestartSec=10s` | Задержка перед перезапуском |

---

## 🔄 Обновление сервиса

### После изменения файла сервиса

```bash
# Перезагрузить конфигурацию systemd
sudo systemctl daemon-reload

# Перезапустить сервис
sudo systemctl restart elia-platform
```

### Обновление приложения

```bash
# Через systemd (автоматически подтянет новый образ)
sudo systemctl restart elia-platform

# Или вручную
cd /opt/elia-platform
docker compose pull
sudo systemctl restart elia-platform
```

---

## 🐛 Устранение неполадок

### Сервис не запускается

```bash
# Проверить логи
sudo journalctl -u elia-platform -n 50

# Проверить статус Docker
sudo systemctl status docker

# Проверить Docker Compose файл
cd /opt/elia-platform
docker compose config
```

### Проверка зависимостей

```bash
# Убедиться что Docker работает
sudo systemctl is-active docker

# Проверить сеть
ping -c 3 8.8.8.8

# Проверить порты
sudo netstat -tlnp | grep :80
```

### Сброс сервиса

```bash
# Остановить сервис
sudo systemctl stop elia-platform

# Очистить Docker
cd /opt/elia-platform
docker compose down --volumes

# Запустить заново
sudo systemctl start elia-platform
```

---

## 📈 Мониторинг производительности

### Использование ресурсов

```bash
# Статус systemd сервиса
systemctl status elia-platform

# Статус Docker контейнера
docker stats elia-platform --no-stream

# Системные ресурсы
free -h
df -h
```

### Проверка здоровья приложения

```bash
# Health check
curl http://localhost/health

# Полная проверка
curl -v http://localhost/health
```

---

## 🔐 Безопасность

### Настройки безопасности в сервисе

- `PrivateTmp=yes` — изолированная временная директория
- `NoNewPrivileges=yes` — запрет повышения привилегий
- `User=root` — запуск от root (требуется для Docker)

### Рекомендации

1. Регулярно обновляйте образ Docker
2. Мониторьте логи на предмет ошибок
3. Настройте backup базы данных
4. Используйте firewall для ограничения доступа

---

## 📝 Скрипты для автоматизации

### Создайте алиасы для удобства

Добавьте в `~/.bashrc` или `~/.zshrc`:

```bash
alias elia-start='sudo systemctl start elia-platform'
alias elia-stop='sudo systemctl stop elia-platform'
alias elia-restart='sudo systemctl restart elia-platform'
alias elia-status='sudo systemctl status elia-platform'
alias elia-logs='sudo journalctl -u elia-platform -f'
```

После этого можно использовать:

```bash
elia-status    # Проверить статус
elia-logs      # Смотреть логи
elia-restart   # Перезапустить
```

---

## 🔄 Интеграция с другими сервисами

### Запуск после PostgreSQL (если используете)

Если в будущем переключитесь на PostgreSQL:

```ini
[Unit]
After=docker.service postgresql.service network-online.target
```

### Зависимости от сети

Сервис настроен на ожидание сети:

```ini
After=network-online.target
Wants=network-online.target
```

---

## 📚 Дополнительные команды

```bash
# Показать все сервисы Elia
systemctl list-units --all | grep elia

# Показать зависимости
systemctl list-dependencies elia-platform

# Показать свойства
systemctl show elia-platform

# Редактировать сервис
sudo systemctl edit elia-platform --full
```

---

## 🎯 Проверочный чек-лист

После установки проверьте:

- [ ] Сервис запущен: `systemctl is-active elia-platform`
- [ ] Автозапуск включен: `systemctl is-enabled elia-platform`
- [ ] Приложение доступно: `curl http://localhost/health`
- [ ] Логи без ошибок: `journalctl -u elia-platform -n 20`
- [ ] Docker контейнер работает: `docker ps | grep elia-platform`

---

## 🔗 См. также

- [Управление сервером](../scripts/README.md)
- [Docker руководство](DOCKER_GUIDE.md)
- [Развёртывание на Ubuntu](UBUNTU_DEPLOYMENT.md)
- [SSH настройка](SSH_SETUP.md)

---

**Дата создания**: 27 октября 2025  
**Сервер**: 43.245.224.114  
**Статус**: ✅ Активен и настроен

