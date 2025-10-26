# 🚀 Быстрый старт — Elia AI Platform

## Вариант 1: Автоматический запуск (рекомендуется)

### Linux / MacOS

```bash
# 1. Инициализация и установка
bash scripts/init.sh

# 2. Запуск приложения
source venv/bin/activate
python -m uvicorn app.main:app --reload

# 3. Откройте http://localhost:8000
```

### Windows

```powershell
# 1. Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Скопировать конфигурацию
copy .env.example .env

# 4. Загрузить тестовые данные
python -m app.fixtures

# 5. Запустить сервер
python -m uvicorn app.main:app --reload

# 6. Откройте http://localhost:8000
```

---

## Вариант 2: Docker (самый простой)

```bash
# 1. Собрать и запустить
docker-compose up -d --build

# 2. Загрузить тестовые данные
docker-compose exec elia-app python -m app.fixtures

# 3. Откройте http://localhost:8000

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

---

## ✅ Проверка работоспособности

После запуска проверьте:

1. **Главная страница**: http://localhost:8000
2. **API документация**: http://localhost:8000/docs
3. **Health check**: http://localhost:8000/health

---

## 🧪 Запуск тестов

```bash
# Все тесты
pytest

# Только API тесты
pytest -m api

# Только E2E тесты
pytest -m e2e

# С покрытием кода
pytest --cov=app
```

Или через скрипт:

```bash
bash scripts/test.sh        # Все тесты
bash scripts/test.sh api    # Только API
bash scripts/test.sh e2e    # Только E2E
bash scripts/test.sh coverage  # С покрытием
```

---

## 📊 Тестовые данные

После загрузки fixtures в системе будет:

- **12 пациентов** с различными заболеваниями
- **12 приёмов** на разные даты
- **Показатели здоровья** для каждого пациента
- **Хронические и последние заболевания**

### Примеры пациентов:

- Иванов Иван Алексеевич (активный приём)
- Петрова Милена Игоревна
- Эцкерев Александр Владимирович
- Малинин Илья Авдотьевич
- И другие...

---

## 🎯 Основные сценарии использования

### 1. Просмотр списка пациентов
- Откройте главную страницу
- Увидите карточки приёмов, сгруппированные по датам
- Используйте поиск для фильтрации

### 2. Работа с карточкой пациента
- Кликните на карточку пациента
- Переключайтесь между вкладками:
  - **Цифровой портрет** — медицинские данные
  - **Анамнез** — заполнение отчёта
  - **Стенограмма** — загрузка аудио

### 3. Заполнение анамнеза
- Откройте вкладку "Анамнез"
- Заполните поля формы
- Нажмите "Сохранить черновик"
- Или "Занести в МИС" для имитации отправки

### 4. Загрузка аудио
- Откройте вкладку "Стенограмма"
- Перетащите аудиофайл или выберите через кнопку
- Поддерживаются форматы: MP3, WAV
- Нажмите "Транскрибировать" для имитации обработки

---

## 🛠 Полезные команды

### Разработка

```bash
# Запуск с автоперезагрузкой
uvicorn app.main:app --reload

# Проверка кода
black app/ tests/
isort app/ tests/
mypy app/

# Просмотр логов
tail -f app.log
```

### База данных

```bash
# Пересоздать БД с тестовыми данными
rm elia.db
python -m app.fixtures

# Подключиться к SQLite
sqlite3 elia.db
```

### Docker

```bash
# Пересобрать образ
docker-compose build --no-cache

# Просмотр контейнеров
docker-compose ps

# Вход в контейнер
docker-compose exec elia-app bash

# Очистка
docker-compose down -v
```

---

## ❓ Частые проблемы

### Порт уже занят

```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Ошибки импорта

```bash
# Переустановить зависимости
pip install --upgrade -r requirements.txt
```

### База данных заблокирована

```bash
# Остановить все процессы и удалить БД
rm elia.db
python -m app.fixtures
```

---

## 📖 Дополнительная информация

Полная документация: [README.md](README.md)

API документация: http://localhost:8000/docs

Спецификация: [Spec/business.md](Spec/business.md)

---

**Успешной работы! 🎉**

