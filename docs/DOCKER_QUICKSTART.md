# 🚀 Быстрый старт Docker для Elia Platform

## Шаг 1: Создайте .env файл

```bash
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
OPENAI_API_KEY=ваш-ключ-здесь
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
EOF
```

## Шаг 2: Подготовьте директории

```bash
mkdir -p data logs static/uploads
```

## Шаг 3: Если у вас есть существующая БД

```bash
# Переместите текущую БД в папку data
mv elia.db data/
```

## Шаг 4: Соберите и запустите Docker

```bash
# Запустите Docker Desktop (если не запущен)

# Соберите образ
docker-compose build

# Запустите контейнер
docker-compose up -d

# Проверьте работу
curl http://localhost:8000/health
```

## 🔧 Как изменить настройки БЕЗ пересборки Docker

### Изменить любой параметр:

1. Отредактируйте `.env` файл
2. Выполните:

```bash
docker-compose restart
```

Или полностью пересоздайте контейнер:

```bash
docker-compose down
docker-compose up -d
```

**База данных и загруженные файлы НЕ пострадают!**

## 📁 Работа с БД БЕЗ изменения Docker

### Текущая БД автоматически используется

База данных хранится в папке `./data/` на вашем компьютере:
- ✅ Данные сохраняются между перезапусками
- ✅ Можно делать бэкапы: `cp data/elia.db data/backup.db`
- ✅ Можно восстановить: остановить Docker → заменить файл → запустить Docker

### Бэкап БД

```bash
# Простой способ
cp data/elia.db data/elia_backup_$(date +%Y%m%d).db

# Или через sqlite3
sqlite3 data/elia.db ".backup data/backup.db"
```

### Восстановление БД

```bash
docker-compose down
cp data/backup.db data/elia.db
docker-compose up -d
```

### Обновление схемы БД (миграции)

```bash
# Войдите в контейнер
docker exec -it elia-platform bash

# Выполните миграции (если есть)
alembic upgrade head
```

## 📝 Полезные команды

```bash
# Посмотреть логи
docker-compose logs -f

# Остановить
docker-compose down

# Перезапустить
docker-compose restart

# Войти в контейнер
docker exec -it elia-platform bash

# Проверить статус
docker-compose ps
```

## ⚠️ Важно

- Все данные (БД, загрузки, логи) хранятся на вашем компьютере в папках `data/`, `static/uploads/`, `logs/`
- При выполнении `docker-compose down` данные НЕ удаляются
- Только `docker-compose down -v` удалит volumes (НЕ делайте это!)

## 🔄 Обновление приложения

```bash
git pull
docker-compose build
docker-compose up -d
# Данные останутся на месте!
```

Подробная документация: см. `DOCKER_GUIDE.md`

