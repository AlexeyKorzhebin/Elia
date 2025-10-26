# Руководство по использованию Docker для Elia Platform

## 🚀 Быстрый старт

### 1. Подготовка окружения

Перед запуском создайте файл `.env` в корневой директории проекта:

```bash
cp .env.example .env
```

Если `.env.example` не существует, создайте `.env` вручную со следующими параметрами:

```env
# Конфигурация базы данных
DATABASE_URL=sqlite+aiosqlite:///./data/elia.db

# Настройки сервера
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Настройки загрузки файлов
UPLOAD_DIR=static/uploads
MAX_UPLOAD_SIZE=52428800

# Настройки приложения
APP_NAME=Elia AI Platform
VERSION=1.0.0

# Настройки логирования
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_RETENTION_DAYS=30

# OpenAI API
OPENAI_API_KEY=ваш-ключ-openai
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

### 2. Сборка Docker образа

```bash
docker-compose build
```

Или для принудительной пересборки:

```bash
docker-compose build --no-cache
```

### 3. Запуск приложения

```bash
docker-compose up -d
```

Для запуска с выводом логов:

```bash
docker-compose up
```

### 4. Остановка приложения

```bash
docker-compose down
```

## 📁 Работа с базой данных БЕЗ изменения Docker

### Использование существующей базы данных

База данных монтируется через volumes в `docker-compose.yml`:

```yaml
volumes:
  - ./data:/app/data
```

**Это означает:**
- ✅ БД хранится в папке `./data` на вашем хост-компьютере
- ✅ Все изменения в БД сохраняются **вне контейнера**
- ✅ При перезапуске контейнера данные **не теряются**
- ✅ Вы можете изменять БД напрямую (не рекомендуется при запущенном контейнере)

### Сценарии работы с БД:

#### Использовать текущую БД (elia.db в корне)

```bash
# 1. Создайте папку data, если её нет
mkdir -p data

# 2. Переместите текущую БД
mv elia.db data/

# 3. Запустите Docker
docker-compose up -d
```

#### Создать новую БД

```bash
# 1. Создайте папку data
mkdir -p data

# 2. Запустите Docker (БД создастся автоматически)
docker-compose up -d
```

#### Обновление БД (миграции)

```bash
# Войдите в контейнер
docker exec -it elia-platform bash

# Запустите миграции (если есть)
alembic upgrade head

# Или выполните скрипт инициализации
python -m app.database
```

#### Бэкап БД

```bash
# Создайте копию БД
cp data/elia.db data/elia_backup_$(date +%Y%m%d_%H%M%S).db

# Или используйте sqlite3
sqlite3 data/elia.db ".backup data/backup.db"
```

#### Восстановление БД

```bash
# 1. Остановите контейнер
docker-compose down

# 2. Восстановите БД
cp data/elia_backup_XXXXXX.db data/elia.db

# 3. Запустите контейнер
docker-compose up -d
```

## ⚙️ Изменение параметров через .env БЕЗ изменения Docker

### Как это работает

Файл `.env` монтируется в контейнер в режиме **read-only**:

```yaml
volumes:
  - ./.env:/app/.env:ro
```

Также используется директива `env_file`:

```yaml
env_file:
  - .env
```

### Изменение параметров:

1. **Отредактируйте файл `.env`** на хост-системе
2. **Перезапустите контейнер**:

```bash
docker-compose restart
```

Или полностью пересоздайте контейнер (рекомендуется):

```bash
docker-compose down
docker-compose up -d
```

**Важно:** БД и загруженные файлы **не пострадают**, так как они монтируются через volumes!

### Примеры изменений:

#### Изменить порт:

```env
PORT=9000
```

```bash
docker-compose down
docker-compose up -d
```

#### Включить debug режим:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

```bash
docker-compose restart
```

#### Изменить OpenAI ключ:

```env
OPENAI_API_KEY=новый-ключ
```

```bash
docker-compose restart
```

## 📊 Персистентность данных

Все важные данные хранятся вне контейнера:

```yaml
volumes:
  - ./data:/app/data              # База данных
  - ./static/uploads:/app/static/uploads  # Загруженные файлы
  - ./logs:/app/logs              # Логи приложения
  - ./.env:/app/.env:ro           # Конфигурация
```

**Это означает:**
- ✅ Данные не удаляются при `docker-compose down`
- ✅ Данные не удаляются при пересборке образа
- ✅ Вы можете обновить код без потери данных
- ✅ Легко делать бэкапы (просто копируйте папки)

## 🔧 Полезные команды

### Просмотр логов

```bash
# Все логи
docker-compose logs

# Логи в реальном времени
docker-compose logs -f

# Последние 100 строк
docker-compose logs --tail=100
```

### Проверка статуса

```bash
docker-compose ps
```

### Вход в контейнер

```bash
docker exec -it elia-platform bash
```

### Проверка health check

```bash
docker inspect elia-platform | grep -A 10 Health
```

### Очистка

```bash
# Остановить и удалить контейнеры
docker-compose down

# Удалить образы
docker-compose down --rmi all

# Удалить volumes (⚠️ УДАЛИТ ДАННЫЕ!)
docker-compose down -v
```

## 🔄 Обновление приложения

```bash
# 1. Получите новый код
git pull

# 2. Пересоберите образ
docker-compose build

# 3. Перезапустите контейнер
docker-compose up -d

# Данные останутся нетронутыми!
```

## 🐛 Отладка

### Проблема: Контейнер не запускается

```bash
# Проверьте логи
docker-compose logs

# Проверьте конфигурацию
docker-compose config
```

### Проблема: БД не найдена

```bash
# Убедитесь, что папка data существует
mkdir -p data

# Проверьте права доступа
ls -la data/
```

### Проблема: Порт занят

```bash
# Измените порт в .env
PORT=9000

# Перезапустите
docker-compose down
docker-compose up -d
```

## 📝 PostgreSQL (опционально)

Если хотите использовать PostgreSQL вместо SQLite:

1. Раскомментируйте секцию postgres в `docker-compose.yml`
2. Измените `DATABASE_URL` в `.env`:

```env
DATABASE_URL=postgresql+asyncpg://elia:elia_password@postgres:5432/elia
```

3. Перезапустите:

```bash
docker-compose down
docker-compose up -d
```

## 🎯 Рекомендации

1. **Всегда используйте `.env`** для конфигурации
2. **Делайте бэкапы БД** регулярно
3. **Не редактируйте БД** при запущенном контейнере
4. **Используйте `docker-compose restart`** для применения изменений .env
5. **Логи храните** на хосте через volume (уже настроено)

## ✅ Проверка работоспособности

После запуска проверьте:

```bash
# Откройте в браузере
open http://localhost:8000

# Или через curl
curl http://localhost:8000/health
```

Должен вернуться ответ: `{"status":"healthy"}`

