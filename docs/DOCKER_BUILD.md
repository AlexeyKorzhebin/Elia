# 🐳 Сборка Docker образа Elia Platform

## Обзор

Elia Platform собирается в Docker образ для удобного развёртывания на любых серверах. Образ поддерживает несколько архитектур и оптимизирован для продакшн использования.

## Быстрый старт

### Автоматическая сборка и публикация

```bash
# Собрать и загрузить в Docker Hub (для всех платформ)
./scripts/build-and-push.sh --push

# Собрать только для локальной платформы
./scripts/build-and-push.sh --no-buildx --push
```

## Поддерживаемые платформы

По умолчанию образ собирается для:
- **linux/amd64** - серверы x86_64 (большинство VPS)
- **linux/arm64** - ARM серверы (Apple Silicon, Raspberry Pi 4+)

## Сборка образа

### Способ 1: Использование скрипта (рекомендуется)

```bash
# Сборка и публикация для всех платформ
./scripts/build-and-push.sh --push

# Сборка для конкретных платформ
./scripts/build-and-push.sh --platform linux/amd64 --push

# Сборка без кэша
./scripts/build-and-push.sh --no-cache --push

# Только сборка (без публикации)
./scripts/build-and-push.sh
```

### Способ 2: Ручная сборка с buildx (multi-platform)

```bash
# Создать и использовать buildx builder
docker buildx create --name multiplatform-builder --use --bootstrap

# Собрать для всех платформ и загрузить
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f Dockerfile.production \
  -t alekseykorzhebin/elia-platform:latest \
  -t alekseykorzhebin/elia-platform:1.0.0 \
  --push \
  .

# Собрать только для amd64 (для серверов)
docker buildx build \
  --platform linux/amd64 \
  -f Dockerfile.production \
  -t alekseykorzhebin/elia-platform:latest \
  --push \
  .
```

### Способ 3: Обычная сборка (локальная платформа)

```bash
# Собрать для текущей платформы
docker build -f Dockerfile.production \
  -t alekseykorzhebin/elia-platform:latest \
  .

# Загрузить в Docker Hub
docker push alekseykorzhebin/elia-platform:latest
```

## Параметры скрипта build-and-push.sh

```bash
./scripts/build-and-push.sh [опции]

Опции:
  -u, --username USERNAME   Docker Hub username (по умолчанию: alekseykorzhebin)
  -n, --name NAME           Имя образа (по умолчанию: elia-platform)
  -v, --version VERSION     Версия образа (по умолчанию: 1.0.0)
  -t, --tag TAG             Дополнительный тег
  --platform PLATFORMS      Платформы для сборки (по умолчанию: linux/amd64,linux/arm64)
  --no-buildx               Использовать обычный docker build вместо buildx
  --no-cache                Сборка без кэша
  --push                    Загрузить в Docker Hub
  --login                   Войти в Docker Hub
  -h, --help                Показать справку
```

## Примеры использования

### Сборка для продакшн сервера (amd64)

```bash
# Собрать только для amd64 и загрузить
./scripts/build-and-push.sh --platform linux/amd64 --push
```

### Сборка новой версии

```bash
# Собрать версию 1.1.0 с тегами latest и 1.1.0
./scripts/build-and-push.sh -v 1.1.0 --push
```

### Локальная сборка для тестирования

```bash
# Собрать локально без загрузки
./scripts/build-and-push.sh --no-buildx

# Запустить локально
docker run -p 8000:80 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env:ro \
  alekseykorzhebin/elia-platform:latest
```

## Структура Dockerfile

Образ использует multi-stage build для оптимизации размера:

1. **Builder stage** - установка зависимостей Python
2. **Production stage** - финальный образ с приложением

### Основные компоненты:

- **Базовый образ:** `python:3.11-slim`
- **Пользователь:** `elia` (непривилегированный)
- **Рабочая директория:** `/app`
- **Порты:** `80` (внутри контейнера)
- **Health check:** `/health` endpoint

## Требования

- Docker 20.10+ с поддержкой buildx (для multi-platform)
- Docker Hub аккаунт (для публикации)
- Достаточно места на диске (~2GB для сборки)

## Устранение проблем

### Ошибка: "buildx not found"

```bash
# Установить buildx plugin
docker buildx install

# Или использовать Docker Desktop (включает buildx)
```

### Ошибка: "no matching manifest"

Убедитесь, что собираете для правильной платформы:

```bash
# Проверить текущую платформу
docker buildx inspect --bootstrap

# Собрать для конкретной платформы
docker buildx build --platform linux/amd64 ...
```

### Ошибка авторизации в Docker Hub

```bash
# Войти в Docker Hub
docker login

# Или через скрипт
./scripts/build-and-push.sh --login
```

## Оптимизация размера образа

Образ оптимизирован следующими способами:

1. **Multi-stage build** - только необходимые файлы в финальном образе
2. **Slim базовый образ** - `python:3.11-slim` вместо полного образа
3. **Очистка кэша** - удаление временных файлов после установки
4. **Минимальные зависимости** - только необходимые системные пакеты

Размер образа: **~200-300MB** (в зависимости от платформы)

## Версионирование

Образы тегируются следующим образом:

- `latest` - последняя стабильная версия
- `1.0.0` - конкретная версия
- `1.0.0-amd64` - версия для конкретной платформы (опционально)

## CI/CD интеграция

Пример GitHub Actions workflow:

```yaml
name: Build and Push Docker Image

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile.production
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            alekseykorzhebin/elia-platform:latest
            alekseykorzhebin/elia-platform:${{ github.ref_name }}
```

## Дополнительные ресурсы

- [Docker Buildx документация](https://docs.docker.com/buildx/)
- [Multi-platform images](https://docs.docker.com/build/building/multi-platform/)
- [Docker Hub](https://hub.docker.com/r/alekseykorzhebin/elia-platform)

---

**Вернуться к [оглавлению документации](README.md)**

