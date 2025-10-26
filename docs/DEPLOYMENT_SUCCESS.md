# ✅ Успешное развертывание Elia Platform

**Дата:** 26 октября 2025  
**Сервер:** 43.245.224.114  
**URL:** http://43.245.224.114

---

## 🎉 Что было выполнено:

### 1. Docker образ
- ✅ Создан мультиплатформенный образ (AMD64 + ARM64)
- ✅ Загружен на DockerHub: `alekseykorzhebin/elia-platform:latest`
- ✅ Версия: 1.0.0
- ✅ Размер: 863MB

### 2. Развертывание на сервере
- ✅ Docker и docker-compose установлены
- ✅ База данных скопирована и настроена (elia.db)
- ✅ Файл .env настроен с правильными ключами OpenAI
- ✅ Контейнер запущен и работает

### 3. Исправленные проблемы
- ✅ Собран образ для правильной платформы (AMD64)
- ✅ Исправлены права пользователя elia в контейнере
- ✅ Настроен PATH для Python пакетов
- ✅ **Исправлены права доступа к базе данных (UID 999)**
- ✅ Установлены права на директории logs, data, uploads

---

## 📂 Структура на сервере

```
/opt/elia-platform/
├── docker-compose.yml      # Конфигурация Docker Compose
├── .env                    # Переменные окружения (OpenAI ключи)
├── elia.db                 # База данных SQLite (rw-rw-r-- 999:999)
├── data/                   # Данные приложения (999:999)
├── logs/                   # Логи приложения (999:999)
└── static/uploads/         # Загруженные файлы (999:999)
```

---

## ⚙️ Конфигурация (.env)

**Расположение:** `/opt/elia-platform/.env`

```bash
# OpenAI API
OPENAI_API_KEY=sk-MZXVBHuvq1YZqSlQfQ9ZjZJxvaBQYgti
OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1
OPENAI_MODEL=gpt-4o-mini

# Database
DATABASE_URL=sqlite+aiosqlite:///./elia.db

# Server
HOST=0.0.0.0
PORT=80
DEBUG=False
```

---

## 🔧 Управление приложением

### Подключение к серверу
```bash
ssh root@43.245.224.114
# Пароль: N+4tymUGSZ
```

### Основные команды
```bash
# Перейти в директорию приложения
cd /opt/elia-platform

# Посмотреть статус контейнера
docker ps | grep elia-platform

# Посмотреть логи
docker logs elia-platform

# Посмотреть логи в реальном времени
docker logs -f elia-platform

# Перезапустить контейнер
docker-compose restart

# Остановить приложение
docker-compose down

# Запустить приложение
docker-compose up -d

# Обновить до новой версии
docker-compose down
docker pull alekseykorzhebin/elia-platform:latest
docker-compose up -d

# Проверить health check
curl http://localhost/health
```

---

## 🐛 Устранение проблем

### Проблема: "attempt to write a readonly database"

**Причина:** Неправильные права доступа к файлу базы данных

**Решение:**
```bash
cd /opt/elia-platform
docker-compose down
chown 999:999 elia.db
chmod 664 elia.db
docker-compose up -d
```

### Проблема: "Permission denied" при записи в logs

**Причина:** Неправильные права на директории

**Решение:**
```bash
cd /opt/elia-platform
docker-compose down
chown -R 999:999 logs data static/uploads
docker-compose up -d
```

### Проблема: Контейнер перезапускается

**Диагностика:**
```bash
docker logs elia-platform --tail 50
```

**Возможные причины:**
- Неправильные права доступа к файлам
- Отсутствие необходимых директорий
- Ошибки в .env файле

---

## 📊 Мониторинг

### Проверка статуса приложения
```bash
# Health check
curl http://43.245.224.114/health

# Главная страница
curl -I http://43.245.224.114/

# Статус контейнера
docker ps | grep elia-platform

# Использование ресурсов
docker stats elia-platform --no-stream
```

### Логи приложения
```bash
# Последние 100 строк
docker logs elia-platform --tail 100

# Логи с временными метками
docker logs -t elia-platform

# Следить за логами в реальном времени
docker logs -f elia-platform
```

---

## 🔄 Обновление конфигурации

### Изменение переменных окружения

1. Остановить контейнер:
```bash
cd /opt/elia-platform
docker-compose down
```

2. Отредактировать .env:
```bash
nano .env
```

3. Запустить контейнер:
```bash
docker-compose up -d
```

### Изменение OpenAI ключа

```bash
cd /opt/elia-platform
docker-compose down
sed -i 's/OPENAI_API_KEY=.*/OPENAI_API_KEY=новый-ключ/' .env
docker-compose up -d
```

---

## 🔐 Безопасность

### Текущие настройки безопасности
- ✅ Контейнер запущен от непривилегированного пользователя (elia, UID 999)
- ✅ База данных защищена на уровне файловой системы
- ✅ Логи доступны только для чтения
- ⚠️ **Рекомендация:** Настроить firewall для ограничения доступа
- ⚠️ **Рекомендация:** Использовать HTTPS с SSL сертификатом

### Рекомендуемые настройки firewall
```bash
# Разрешить только HTTP и SSH
ufw allow 22/tcp
ufw allow 80/tcp
ufw enable
```

---

## 📈 Производительность

### Текущие характеристики
- **Размер образа:** 863MB
- **RAM:** ~200MB в idle
- **CPU:** Минимальное использование в idle

### Рекомендации по оптимизации
- Регулярно очищать старые логи
- Следить за размером базы данных
- При необходимости увеличить лимиты памяти в docker-compose.yml

---

## 🔗 Полезные ссылки

- **Приложение:** http://43.245.224.114
- **Health Check:** http://43.245.224.114/health
- **Docker Hub:** https://hub.docker.com/r/alekseykorzhebin/elia-platform
- **GitHub:** (добавьте ссылку на репозиторий)

---

## ✅ Проверочный список

После развертывания или обновления проверьте:

- [ ] Приложение отвечает на http://43.245.224.114
- [ ] Health check возвращает `{"status":"ok"}`
- [ ] Контейнер запущен: `docker ps | grep elia-platform`
- [ ] Нет ошибок в логах: `docker logs elia-platform --tail 50`
- [ ] База данных доступна для записи (права 664, владелец 999:999)
- [ ] Директории logs, data, uploads принадлежат пользователю 999
- [ ] Файл .env содержит правильные ключи OpenAI

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker logs elia-platform`
2. Проверьте права доступа к файлам
3. Убедитесь, что контейнер запущен: `docker ps`
4. Проверьте конфигурацию .env

---

**Статус:** ✅ Приложение работает  
**Последнее обновление:** 26 октября 2025, 23:55 UTC  
**Версия образа:** alekseykorzhebin/elia-platform:latest (digest: sha256:0cd87bd...)

