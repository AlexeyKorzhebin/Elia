# Elia AI Platform — MVP

AI-платформа для врача с функциями ведения приёмов, работы с медицинской документацией, загрузки аудиозаписей и формирования отчётов.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

## 📋 Содержание

- [Описание проекта](#описание-проекта)
- [Функционал MVP](#функционал-mvp)
- [Технологии](#технологии)
- [Требования](#требования)
- [Установка и запуск](#установка-и-запуск)
  - [Локальный запуск](#локальный-запуск)
  - [Запуск через Docker](#запуск-через-docker)
- [Структура проекта](#структура-проекта)
- [API документация](#api-документация)
- [Тестирование](#тестирование)
- [Ограничения MVP](#ограничения-mvp)

---

## 📖 Описание проекта

Elia AI Platform — это MVP цифрового рабочего пространства для врача, предназначенного для:

- 👥 Управления списком пациентов и приёмов
- 📊 Просмотра цифрового портрета пациента с ключевыми показателями здоровья
- 📝 Ведения медицинской документации (анамнез)
- 🎙️ Загрузки аудиозаписей приёма
- 🤖 Имитации транскрибации аудио (без реального AI)
- 🏥 Имитации выгрузки отчётов в МИС (без реальной интеграции)

Система создана для тестирования UX и основных бизнес-процессов без реальной интеграции с внешними системами.

---

## ✨ Функционал MVP

### Главный экран — "Мои пациенты"

- ✅ Отображение карточек пациентов с датой и временем приёма
- ✅ Поиск и фильтрация по ФИО
- ✅ Группировка приёмов по датам
- ✅ Подсветка активного приёма

### Карточка пациента

**Вкладка "Цифровой портрет":**
- ✅ Основные данные (пол, возраст, МО, участок)
- ✅ Хронические и последние заболевания
- ✅ Показатели здоровья (гемоглобин, холестерин, ИМТ, ЧСС)

**Вкладка "Анамнез":**
- ✅ Форма для ручного заполнения (цель обращения, жалобы, анамнез)
- ✅ Сохранение черновика
- ✅ Имитация отправки в МИС с анимацией (3 сек)

**Вкладка "Стенограмма":**
- ✅ Загрузка аудиофайлов (MP3, WAV)
- ✅ Аудиоплеер для прослушивания
- ✅ Имитация транскрибации с прогресс-баром (6 сек)
- ✅ Отображение фиктивной транскрипции

---

## 🛠 Технологии

### Backend
- **FastAPI** — современный async веб-фреймворк
- **SQLAlchemy 2.0** — ORM с поддержкой async
- **SQLite** / **PostgreSQL** — база данных
- **Pydantic** — валидация данных
- **Uvicorn** — ASGI сервер

### Frontend
- **Vanilla JavaScript** / **jQuery** — клиентская логика
- **Tailwind CSS** — utility-first CSS фреймворк
- **HTML5** — семантическая разметка

### Testing
- **Pytest** — фреймворк для тестирования
- **Playwright** — E2E тестирование
- **HTTPX** — async HTTP клиент для тестов

### DevOps
- **Docker** — контейнеризация
- **Docker Compose** — оркестрация контейнеров

---

## 📦 Требования

- **Python 3.11+**
- **pip** или **poetry**
- **Docker** и **Docker Compose** (опционально)

---

## 🚀 Установка и запуск

### Локальный запуск

#### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd Elia
```

#### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
# или
venv\Scripts\activate  # Для Windows
```

#### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 4. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` при необходимости:

```env
DATABASE_URL=sqlite+aiosqlite:///./elia.db
HOST=0.0.0.0
PORT=8000
DEBUG=true
UPLOAD_DIR=static/uploads
MAX_UPLOAD_SIZE=52428800
```

#### 5. Инициализация базы данных и загрузка тестовых данных

```bash
python -m app.fixtures
```

Эта команда создаст базу данных и загрузит 10-15 тестовых пациентов с приёмами.

#### 6. Запуск сервера

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Или через main.py:

```bash
python app/main.py
```

#### 7. Открыть в браузере

Перейдите по адресу: **http://localhost:8000**

---

### Запуск через Docker

#### 1. Сборка и запуск контейнеров

```bash
docker-compose up -d --build
```

#### 2. Загрузка тестовых данных

```bash
docker-compose exec elia-app python -m app.fixtures
```

#### 3. Открыть в браузере

Перейдите по адресу: **http://localhost:8000**

#### 4. Остановка контейнеров

```bash
docker-compose down
```

#### 5. Просмотр логов

```bash
docker-compose logs -f elia-app
```

---

## 📁 Структура проекта

```
Elia/
├── app/                         # Backend приложение
│   ├── __init__.py
│   ├── main.py                  # Точка входа FastAPI
│   ├── config.py                # Конфигурация
│   ├── database.py              # Настройки БД
│   ├── models.py                # SQLAlchemy модели
│   ├── schemas.py               # Pydantic схемы
│   ├── crud.py                  # CRUD операции
│   ├── fixtures.py              # Тестовые данные
│   └── api/                     # API endpoints
│       ├── __init__.py
│       ├── patients.py          # /api/patients
│       ├── appointments.py      # /api/appointments
│       └── audio.py             # /api/audio
├── static/                      # Статические файлы
│   ├── css/
│   │   └── styles.css           # Кастомные стили
│   ├── js/
│   │   ├── main.js              # Основная логика
│   │   ├── patients.js          # Список пациентов
│   │   ├── patient-card.js      # Карточка пациента
│   │   └── audio-handler.js     # Обработка аудио
│   └── uploads/                 # Загруженные файлы
├── templates/
│   └── index.html               # HTML шаблон
├── tests/                       # Тесты
│   ├── __init__.py
│   ├── conftest.py              # Pytest конфигурация
│   ├── test_api.py              # API тесты
│   └── test_e2e.py              # E2E тесты
├── Spec/                        # Спецификации и дизайн
│   └── business.md              # Бизнес требования
├── requirements.txt             # Python зависимости
├── pytest.ini                   # Конфигурация pytest
├── Dockerfile                   # Docker образ
├── docker-compose.yml           # Docker Compose конфигурация
├── .env.example                 # Пример переменных окружения
├── .gitignore                   # Git ignore файл
└── README.md                    # Документация
```

---

## 📚 API документация

После запуска сервера API документация доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные endpoints

#### Пациенты

- `GET /api/patients` — список пациентов
- `GET /api/patients/{id}` — детали пациента
- `GET /api/patients/{id}/digital-portrait` — цифровой портрет

#### Приёмы

- `GET /api/appointments` — список приёмов
- `GET /api/appointments/{id}` — детали приёма
- `GET /api/appointments/{id}/report` — получить отчёт
- `POST /api/appointments/{id}/report` — создать/обновить отчёт
- `POST /api/appointments/{id}/submit-to-mis` — отправить в МИС (имитация)

#### Аудиофайлы

- `POST /api/audio/upload` — загрузить аудиофайл
- `POST /api/audio/{id}/transcribe` — транскрибировать (имитация)
- `GET /api/audio/{id}` — информация об аудиофайле
- `GET /api/audio/{id}/download` — скачать/проиграть аудио

---

## 🧪 Тестирование

### Запуск всех тестов

```bash
pytest
```

### Запуск только API тестов

```bash
pytest -m api
```

### Запуск E2E тестов

```bash
pytest -m e2e
```

### Запуск с подробным выводом

```bash
pytest -v
```

### Генерация отчёта о покрытии

```bash
pytest --cov=app --cov-report=html
```

### Установка Playwright браузеров (для E2E тестов)

```bash
playwright install
```

---

## ⚠️ Ограничения MVP

Данная версия является MVP (Minimum Viable Product) и имеет следующие ограничения:

- ❌ **Нет авторизации пользователей** — любой может получить доступ
- ❌ **Нет реальной транскрибации** — используется фиктивный текст
- ❌ **Нет интеграции с МИС** — только имитация отправки
- ❌ **Нет реального AI анализа** — все подсказки статичные
- ❌ **Нет обработки аудио** — файлы только сохраняются
- ⚠️ **SQLite по умолчанию** — для продакшена рекомендуется PostgreSQL

### Миграция на PostgreSQL

1. Установите PostgreSQL
2. Создайте базу данных:
   ```sql
   CREATE DATABASE elia;
   ```
3. Обновите `DATABASE_URL` в `.env`:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/elia
   ```
4. Установите драйвер:
   ```bash
   pip install asyncpg
   ```
5. Перезапустите приложение

---

## 👨‍💻 Разработка

### Добавление новых зависимостей

```bash
pip install <package>
pip freeze > requirements.txt
```

### Запуск в режиме разработки

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Форматирование кода

```bash
black app/ tests/
isort app/ tests/
```

### Проверка типов

```bash
mypy app/
```

---

## 📝 Changelog

### Version 1.0.0 (26.10.2025)
- ✅ Реализован MVP функционал
- ✅ Список пациентов и приёмов
- ✅ Цифровой портрет пациента
- ✅ Форма анамнеза
- ✅ Загрузка и транскрибация аудио (имитация)
- ✅ Отправка в МИС (имитация)
- ✅ API тесты (pytest)
- ✅ E2E тесты (Playwright)
- ✅ Docker поддержка
- ✅ Документация

---

## 📄 Лицензия

MIT License

---

## 🤝 Контакты

Для вопросов и предложений:
- Email: support@elia-platform.ru
- Telegram: @elia_support

---

**Сделано с ❤️ для врачей**

