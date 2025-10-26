# 🐳 Как собрать Docker для Elia Platform

## ✅ Что было сделано

1. ✅ Обновлён `Dockerfile` - убрана зависимость от .env.example
2. ✅ Обновлён `docker-compose.yml` - настроена работа с .env и volumes
3. ✅ Создан скрипт автоматической настройки `setup-docker.sh`
4. ✅ Настроены volumes для персистентности:
   - `./data/` → база данных
   - `./static/uploads/` → загруженные файлы
   - `./logs/` → логи приложения
   - `./.env` → конфигурация (read-only)

## 🚀 Как собрать и запустить (3 команды)

### Способ 1: Автоматический (рекомендуется)

```bash
./setup-docker.sh
docker-compose build
docker-compose up -d
```

### Способ 2: Ручной

```bash
# 1. Создайте .env файл
cat > .env << 'EOF'
DATABASE_URL=sqlite+aiosqlite:///./data/elia.db
HOST=0.0.0.0
PORT=8000
DEBUG=false
UPLOAD_DIR=static/uploads
MAX_UPLOAD_SIZE=52428800
APP_NAME=Elia AI Platform
VERSION=1.0.0
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_RETENTION_DAYS=30
OPENAI_API_KEY=ваш-ключ-openai
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
EOF

# 2. Создайте директории
mkdir -p data logs static/uploads

# 3. Если есть текущая БД, переместите её
mv elia.db data/  # опционально, если есть elia.db в корне

# 4. Соберите Docker образ
docker-compose build

# 5. Запустите контейнер
docker-compose up -d

# 6. Проверьте работу
curl http://localhost:8000/health
```

## 🗄️ Использование текущей базы данных БЕЗ изменения Docker

### Как это работает

В `docker-compose.yml` настроен volume:

```yaml
volumes:
  - ./data:/app/data  # БД монтируется из хост-системы
```

**Это означает:**
- ✅ БД находится на вашем компьютере в папке `./data/`
- ✅ Все изменения в БД сохраняются ВНЕ контейнера
- ✅ При `docker-compose down` данные НЕ удаляются
- ✅ При пересборке образа данные НЕ теряются
- ✅ Можно изменять БД напрямую (когда контейнер остановлен)

### Сценарии:

#### 1. Использовать существующую БД

```bash
# Если у вас есть elia.db в корне проекта:
mkdir -p data
mv elia.db data/
docker-compose up -d
```

#### 2. Создать новую БД

```bash
# БД создастся автоматически при первом запуске
mkdir -p data
docker-compose up -d
```

#### 3. Обновить/мигрировать БД

```bash
# Войдите в контейнер
docker exec -it elia-platform bash

# Выполните миграции (если есть Alembic)
alembic upgrade head

# Или выполните скрипт инициализации
python -m app.database

# Выйдите из контейнера
exit
```

#### 4. Сделать бэкап БД

```bash
# Простое копирование
cp data/elia.db data/backup_$(date +%Y%m%d_%H%M%S).db

# Или через sqlite3
sqlite3 data/elia.db ".backup data/backup.db"
```

#### 5. Восстановить БД из бэкапа

```bash
# 1. Остановите контейнер
docker-compose down

# 2. Восстановите БД
cp data/backup_YYYYMMDD_HHMMSS.db data/elia.db

# 3. Запустите контейнер
docker-compose up -d
```

## ⚙️ Изменение параметров через .env БЕЗ изменения Docker

### Как это работает

В `docker-compose.yml` настроено:

```yaml
env_file:
  - .env                    # Загрузка переменных окружения
volumes:
  - ./.env:/app/.env:ro     # Монтирование файла (read-only)
```

**Это означает:**
- ✅ Файл `.env` находится на вашем компьютере
- ✅ Можно изменять параметры без пересборки Docker
- ✅ Изменения применяются через `docker-compose restart`

### Как изменить параметры:

1. **Отредактируйте файл `.env`** на вашем компьютере
2. **Перезапустите контейнер:**

```bash
docker-compose restart
```

Или более безопасно (рекомендуется):

```bash
docker-compose down
docker-compose up -d
```

**ВАЖНО:** База данных, загруженные файлы и логи НЕ пострадают!

### Примеры изменений:

#### Изменить порт

```bash
# Отредактируйте .env
nano .env
# Измените: PORT=9000

# Перезапустите
docker-compose down
docker-compose up -d

# Проверьте
curl http://localhost:9000/health
```

#### Включить режим отладки

```bash
# Отредактируйте .env
echo "DEBUG=true" >> .env
echo "LOG_LEVEL=DEBUG" >> .env

# Перезапустите
docker-compose restart

# Логи будут более подробными
docker-compose logs -f
```

#### Изменить OpenAI API ключ

```bash
# Отредактируйте .env
nano .env
# Измените: OPENAI_API_KEY=новый-ключ

# Перезапустите
docker-compose restart
```

#### Изменить модель OpenAI

```bash
# Отредактируйте .env
nano .env
# Измените: OPENAI_MODEL=gpt-3.5-turbo

# Перезапустите
docker-compose restart
```

## 📊 Что хранится ВНЕ Docker (персистентно)

Все важные данные монтируются через volumes:

```yaml
volumes:
  - ./data:/app/data                      # База данных SQLite
  - ./static/uploads:/app/static/uploads  # Загруженные аудио-файлы
  - ./logs:/app/logs                      # Логи приложения
  - ./.env:/app/.env:ro                   # Конфигурация (read-only)
```

**Гарантии:**
- ✅ Данные НЕ удаляются при `docker-compose down`
- ✅ Данные НЕ удаляются при `docker-compose build`
- ✅ Данные НЕ теряются при пересоздании контейнера
- ✅ Легко делать бэкапы (просто копируйте папки)

⚠️ **ВНИМАНИЕ:** Только команда `docker-compose down -v` удалит volumes (НЕ используйте её!)

## 🔄 Обновление приложения

```bash
# 1. Получите новый код
git pull

# 2. Пересоберите образ
docker-compose build

# 3. Пересоздайте контейнер
docker-compose down
docker-compose up -d

# Данные (БД, загрузки, логи) останутся на месте!
```

## 🔧 Полезные команды

```bash
# Просмотр логов
docker-compose logs -f

# Проверка статуса
docker-compose ps

# Вход в контейнер
docker exec -it elia-platform bash

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Пересборка без кэша
docker-compose build --no-cache
```

## ✅ Проверка работоспособности

```bash
# Проверьте статус контейнера
docker-compose ps

# Проверьте health check
curl http://localhost:8000/health
# Ожидается: {"status":"healthy"}

# Откройте в браузере
open http://localhost:8000
```

## 📚 Дополнительная документация

Файл | Описание
-----|----------
`DOCKER_README.md` | Полная итоговая инструкция
`DOCKER_QUICKSTART.md` | Быстрый старт за 5 минут
`DOCKER_GUIDE.md` | Подробное руководство со всеми деталями
`docker-cheatsheet.txt` | Шпаргалка с командами
`setup-docker.sh` | Скрипт автоматической настройки

## 🐛 Устранение проблем

### Docker daemon не запущен

```bash
# Запустите Docker Desktop
open -a Docker

# Подождите пока запустится и повторите
docker-compose build
```

### Порт уже используется

```bash
# Измените порт в .env
echo "PORT=9000" > .env

# Перезапустите
docker-compose down
docker-compose up -d
```

### База данных не найдена

```bash
# Убедитесь, что директория существует
mkdir -p data

# Проверьте настройки в .env
cat .env | grep DATABASE_URL
```

### Проблемы с правами доступа

```bash
# Проверьте права
ls -la data/ static/uploads/ logs/

# Исправьте при необходимости
chmod -R 755 data static/uploads logs
```

## 🎯 Итого

**Вы можете:**
- ✅ Собрать Docker образ: `docker-compose build`
- ✅ Использовать текущую БД: переместить в `./data/`
- ✅ Обновлять БД: войти в контейнер и выполнить миграции
- ✅ Менять параметры .env: редактировать файл и сделать `restart`
- ✅ Всё это БЕЗ изменения Docker и БЕЗ потери данных!

---

**Готово к использованию! Запустите:**

```bash
./setup-docker.sh
docker-compose build
docker-compose up -d
```

