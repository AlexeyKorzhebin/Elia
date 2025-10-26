# ✅ Образ Elia Platform успешно загружен на DockerHub

**Дата загрузки:** 26 октября 2025  
**Docker Hub репозиторий:** https://hub.docker.com/r/alekseykorzhebin/elia-platform

## 📦 Загруженные образы

- `alekseykorzhebin/elia-platform:1.0.0` - версия 1.0.0
- `alekseykorzhebin/elia-platform:latest` - последняя версия

**Размер образа:** 863MB  
**Docker Image ID:** d296abdb3a2f

---

## 🚀 Использование образа

### Вариант 1: Docker Compose (рекомендуется)

```bash
docker-compose -f docker-compose.hub.yml up -d
```

### Вариант 2: Прямой запуск Docker

```bash
docker run -d \
  --name elia-platform \
  -p 80:80 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/static/uploads:/app/static/uploads \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  alekseykorzhebin/elia-platform:latest
```

### Вариант 3: Использование конкретной версии

```bash
docker pull alekseykorzhebin/elia-platform:1.0.0
docker run -d \
  --name elia-platform \
  -p 80:80 \
  --env-file .env \
  alekseykorzhebin/elia-platform:1.0.0
```

---

## 📥 Скачивание образа

```bash
# Последняя версия
docker pull alekseykorzhebin/elia-platform:latest

# Конкретная версия
docker pull alekseykorzhebin/elia-platform:1.0.0
```

---

## 🔄 Обновление образа

### Шаг 1: Остановить текущий контейнер

```bash
docker-compose -f docker-compose.hub.yml down
```

### Шаг 2: Скачать обновление

```bash
docker pull alekseykorzhebin/elia-platform:latest
```

### Шаг 3: Запустить обновленную версию

```bash
docker-compose -f docker-compose.hub.yml up -d
```

---

## 🔨 Сборка и публикация новой версии

Для загрузки новой версии образа используйте скрипт:

```bash
# Сборка и загрузка
./scripts/build-and-push.sh --push

# Сборка с новой версией
./scripts/build-and-push.sh -v 1.1.0 --push

# Сборка без кэша
./scripts/build-and-push.sh --no-cache --push
```

---

## 🔑 Авторизация в DockerHub

Для загрузки новых версий необходима авторизация:

```bash
docker login -u alekseykorzhebin
```

При запросе пароля используйте **Personal Access Token** с правами на запись (Read, Write, Delete).

**Создать токен:** https://hub.docker.com/settings/security

---

## 📋 Конфигурация

### docker-compose.hub.yml

```yaml
services:
  elia-app:
    image: alekseykorzhebin/elia-platform:latest
    container_name: elia-platform
    ports:
      - "${PORT:-80}:80"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./static/uploads:/app/static/uploads
      - ./logs:/app/logs
      - ./.env:/app/.env:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

---

## 🌐 Доступ к платформе

После запуска контейнера платформа будет доступна по адресу:

- **Локально:** http://localhost
- **На сервере:** http://your-server-ip

---

## 🐛 Устранение неполадок

### Проверка статуса контейнера

```bash
docker ps
docker logs elia-platform
```

### Перезапуск контейнера

```bash
docker restart elia-platform
```

### Полная переустановка

```bash
docker-compose -f docker-compose.hub.yml down
docker rmi alekseykorzhebin/elia-platform:latest
docker pull alekseykorzhebin/elia-platform:latest
docker-compose -f docker-compose.hub.yml up -d
```

---

## 📊 Информация об образе

```bash
# Проверить доступность на DockerHub
docker search alekseykorzhebin/elia-platform

# Показать локальные образы
docker images alekseykorzhebin/elia-platform

# Информация о слоях образа
docker history alekseykorzhebin/elia-platform:latest
```

---

## 🔗 Полезные ссылки

- **DockerHub репозиторий:** https://hub.docker.com/r/alekseykorzhebin/elia-platform
- **Создание Access Token:** https://hub.docker.com/settings/security
- **Документация Docker:** https://docs.docker.com/

---

## ✨ Особенности образа

- ✅ Multi-stage build для оптимизации размера
- ✅ Запуск от непривилегированного пользователя (elia)
- ✅ Health check для контроля состояния
- ✅ Поддержка volume для данных и логов
- ✅ Конфигурация через переменные окружения
- ✅ Автоматический перезапуск при сбое

---

**🎉 Готово! Elia Platform успешно опубликован на DockerHub и готов к использованию!**

