# 🐳 Docker для Elia Platform - Итоговая инструкция

## ✅ Что было сделано

1. ✅ Обновлён `docker-compose.yml` для работы с `.env` файлом
2. ✅ Настроены volumes для персистентности данных (БД, загрузки, логи)
3. ✅ Создан скрипт автоматической настройки `setup-docker.sh`
4. ✅ Создана подробная документация

## 🚀 Как запустить (3 команды)

### Вариант 1: Автоматическая настройка (рекомендуется)

```bash
./setup-docker.sh
docker-compose build
docker-compose up -d
```

### Вариант 2: Ручная настройка

```bash
# 1. Создайте .env файл (см. ниже пример)
nano .env

# 2. Создайте директории
mkdir -p data logs static/uploads

# 3. Если есть текущая БД, переместите её
mv elia.db data/  # опционально

# 4. Соберите и запустите
docker-compose build
docker-compose up -d
```

## 📝 Пример .env файла

Создайте файл `.env` в корне проекта:

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

# OpenAI (замените на ваш ключ!)
OPENAI_API_KEY=sk-ваш-ключ-здесь
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

## 🗄️ База данных БЕЗ изменения Docker

### Как это работает

В `docker-compose.yml` настроен volume:

```yaml
volumes:
  - ./data:/app/data  # БД хранится здесь
```

**Это означает:**
- ✅ БД находится в папке `./data/` на вашем компьютере
- ✅ Все изменения сохраняются вне контейнера
- ✅ При пересборке Docker данные НЕ теряются
- ✅ При `docker-compose down` данные НЕ удаляются

### Использование текущей БД

```bash
# Если у вас есть elia.db в корне:
mkdir -p data
mv elia.db data/
docker-compose up -d
```

### Обновление БД

```bash
# Войдите в контейнер
docker exec -it elia-platform bash

# Выполните миграции (если есть)
alembic upgrade head

# Или инициализируйте БД
python -m app.database
```

### Бэкап и восстановление

```bash
# Бэкап
cp data/elia.db data/backup_$(date +%Y%m%d).db

# Восстановление
docker-compose down
cp data/backup_YYYYMMDD.db data/elia.db
docker-compose up -d
```

## ⚙️ Изменение параметров БЕЗ изменения Docker

### Как это работает

В `docker-compose.yml` настроено:

```yaml
env_file:
  - .env
volumes:
  - ./.env:/app/.env:ro  # read-only
```

### Изменение любых параметров

1. **Отредактируйте `.env`** файл
2. **Перезапустите контейнер:**

```bash
docker-compose restart
```

Или полностью пересоздайте (безопаснее):

```bash
docker-compose down
docker-compose up -d
```

**ВАЖНО:** База данных и загруженные файлы НЕ пострадают!

### Примеры изменений

#### Сменить порт

```env
PORT=9000
```

```bash
docker-compose down && docker-compose up -d
```

#### Включить отладку

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

```bash
docker-compose restart
```

#### Изменить OpenAI ключ

```env
OPENAI_API_KEY=новый-ключ
```

```bash
docker-compose restart
```

## 📊 Что хранится ВНЕ Docker (персистентно)

```yaml
volumes:
  - ./data:/app/data                      # База данных
  - ./static/uploads:/app/static/uploads  # Загруженные файлы
  - ./logs:/app/logs                      # Логи приложения
  - ./.env:/app/.env:ro                   # Конфигурация
```

**Все эти данные:**
- ✅ Не удаляются при `docker-compose down`
- ✅ Не удаляются при пересборке образа
- ✅ Доступны на хост-системе
- ✅ Легко делать бэкапы

## 🔧 Полезные команды

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск (применить изменения .env)
docker-compose restart

# Логи
docker-compose logs -f

# Статус
docker-compose ps

# Вход в контейнер
docker exec -it elia-platform bash

# Пересборка
docker-compose build --no-cache
```

## 🔄 Обновление кода

```bash
git pull
docker-compose build
docker-compose down
docker-compose up -d
```

**Данные (БД, загрузки, логи) останутся нетронутыми!**

## 🐛 Устранение неполадок

### Docker daemon не запущен

```bash
# Запустите Docker Desktop
open -a Docker
```

### Порт занят

```bash
# Измените порт в .env
echo "PORT=9000" >> .env

# Перезапустите
docker-compose down
docker-compose up -d
```

### БД не найдена

```bash
# Создайте директорию
mkdir -p data

# Проверьте путь в .env
cat .env | grep DATABASE_URL
```

### Проблемы с правами доступа

```bash
# Проверьте права
ls -la data/ static/uploads/ logs/

# Исправьте при необходимости
chmod -R 755 data static/uploads logs
```

## 📚 Документация

- **`DOCKER_QUICKSTART.md`** - быстрый старт (5 минут)
- **`DOCKER_GUIDE.md`** - полное руководство (все детали)
- **`setup-docker.sh`** - скрипт автоматической настройки

## 🎯 Важные моменты

1. **Файл `.env` критически важен** - без него контейнер не запустится
2. **БД хранится в `./data/`** - делайте бэкапы регулярно
3. **Изменения .env применяются через restart** - не нужно пересобирать образ
4. **Данные персистентны** - пересборка Docker безопасна
5. **Логи доступны** в `./logs/` и через `docker-compose logs`

## ✅ Проверка работы

```bash
# Проверьте статус
docker-compose ps

# Проверьте health
curl http://localhost:8000/health

# Откройте в браузере
open http://localhost:8000
```

Должен быть ответ: `{"status":"healthy"}`

---

**Готово! Теперь вы можете:**
- ✅ Использовать существующую БД без потери данных
- ✅ Обновлять БД без изменения Docker
- ✅ Менять любые параметры через `.env`
- ✅ Делать бэкапы и восстановление
- ✅ Обновлять код без потери данных

