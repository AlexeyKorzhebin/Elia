# Elia AI Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-yellow)

**Интеллектуальная платформа для цифровизации медицинских приёмов**

Elia AI Platform — это современное веб-приложение для врачей, которое упрощает ведение медицинской документации, работу с пациентами и автоматизирует рутинные задачи с помощью искусственного интеллекта.

---

## 🌟 Возможности

- 👥 **Управление пациентами** — полная информация о пациентах и их приёмах
- 📊 **Цифровой портрет** — ключевые показатели здоровья в удобном виде
- 🎙️ **Работа с аудио** — загрузка и транскрибация записей приёма
- 🤖 **AI-ассистент** — автоматическое извлечение анамнеза из разговора
- 📝 **Медицинская документация** — ведение записей и отчётов
- 📄 **Генерация PDF** — выгрузка отчётов в удобном формате
- 🏥 **Интеграция с МИС** — отправка данных в медицинские информационные системы

---

## 🚀 Быстрый старт

### С помощью Docker (рекомендуется)

```bash
# Клонировать репозиторий
git clone <repository-url>
cd Elia

# Запустить с Docker Compose
docker compose up -d

# Загрузить тестовые данные
docker compose exec elia-app python -m app.fixtures

# Открыть в браузере
open http://localhost:8000
```

### Локальный запуск

```bash
# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env

# Загрузить тестовые данные
python -m app.fixtures

# Запустить сервер
python -m uvicorn app.main:app --reload --port 8000
```

---

## 🛠 Технологический стек

### Backend
- **FastAPI** — современный асинхронный веб-фреймворк
- **SQLAlchemy 2.0** — ORM с поддержкой async
- **SQLite/PostgreSQL** — гибкая работа с базами данных
- **OpenAI API** — интеграция с GPT-4 для AI функций
- **ReportLab** — генерация PDF отчётов

### Frontend
- **Vanilla JavaScript** — быстрый и современный клиент
- **Tailwind CSS** — адаптивный и красивый дизайн
- **HTML5** — семантическая разметка

### DevOps
- **Docker** — контейнеризация приложения
- **Docker Compose** — оркестрация сервисов
- **Pytest** — автоматическое тестирование
- **GitHub Actions** — CI/CD (планируется)

---

## 📚 Документация

Полная документация проекта находится в папке [`docs/`](docs/):

### Начало работы
- [📖 Быстрый старт](docs/QUICKSTART.md) — начните работу за 5 минут
- [🤖 Настройка OpenAI](docs/OPENAI_SETUP.md) — подключение AI функций
- [🔧 Настройка OpenAI (краткая)](docs/QUICKSTART_OPENAI.md) — быстрая настройка

### Развёртывание
- [🐳 Docker — краткое руководство](docs/DOCKER_QUICKSTART.md)
- [🐳 Docker — полное руководство](docs/DOCKER_GUIDE.md)
- [📦 Docker Hub — публикация образов](docs/DOCKER_HUB_GUIDE.md)
- [🖥️ Развёртывание на Ubuntu](docs/UBUNTU_DEPLOYMENT.md)
- [🔐 Настройка SSH доступа](docs/SSH_SETUP.md)

### Разработка
- [📊 Статус проекта](docs/PROJECT_STATUS.md)
- [🎨 Дизайн-система](docs/DESIGN_SYSTEM.md)
- [📝 Логирование](docs/LOGGING_IMPLEMENTATION.md)
- [🏗️ Структура проекта](docs/SUMMARY.md)

### Функционал
- [📄 Генерация PDF отчётов](docs/PDF_DOWNLOAD_FEATURE.md)
- [🎙️ Редактирование транскрипций](docs/TRANSCRIPTION_EDITING.md)
- [🐛 Исправление багов](docs/BUGFIX_ANAMNESIS.md)

### Деплой и поддержка
- [✅ Успешное развёртывание](docs/DEPLOYMENT_SUCCESS.md)
- [🚀 Параметры деплоя](docs/DEPLOY_PARAMETERS.md)
- [📋 Итоги развёртывания](docs/UBUNTU_DEPLOYMENT_SUMMARY.md)

---

## 🎯 Основные функции

### 1. Список пациентов
Удобный интерфейс для просмотра всех пациентов и их приёмов с возможностью поиска и фильтрации.

### 2. Цифровой портрет пациента
Полная медицинская информация в одном месте:
- Личные данные
- Хронические заболевания
- История обращений
- Ключевые показатели здоровья

### 3. Работа с аудиозаписями
- Загрузка аудио приёма
- Автоматическая транскрибация с помощью AI
- Редактирование текста
- Сохранение и экспорт

### 4. Автоматический анамнез
AI-ассистент анализирует разговор и автоматически формирует:
- Цель обращения
- Жалобы пациента
- Медицинский анамнез

### 5. Генерация отчётов
Создание профессиональных медицинских отчётов в формате PDF с поддержкой кириллицы.

---

## 📦 Управление сервером

Для удобной работы с удалённым сервером используйте скрипты из папки `scripts/`:

```bash
# Проверить статус
./scripts/server-status.sh

# Посмотреть логи
./scripts/server-logs.sh

# Перезапустить приложение
./scripts/server-restart.sh

# Обновить до последней версии
./scripts/update-server.sh
```

Подробнее: [`scripts/README.md`](scripts/README.md)

---

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# API тесты
pytest tests/test_api.py

# E2E тесты
pytest tests/test_e2e.py

# С покрытием кода
pytest --cov=app
```

---

## 🔒 Безопасность

- Используйте `.env` для хранения секретных данных
- Настройте SSH ключи для доступа к серверу (см. [`docs/SSH_SETUP.md`](docs/SSH_SETUP.md))
- Регулярно обновляйте зависимости
- Используйте HTTPS в production

---

## 📊 API документация

После запуска приложения документация доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🗂 Структура проекта

```
Elia/
├── app/                    # Backend приложение
│   ├── api/               # API endpoints
│   ├── main.py            # Точка входа
│   ├── models.py          # Модели БД
│   └── ...
├── static/                # Статические файлы
│   ├── css/              # Стили
│   ├── js/               # JavaScript
│   └── uploads/          # Загруженные файлы
├── templates/             # HTML шаблоны
├── tests/                 # Автотесты
├── docs/                  # 📚 Документация
├── scripts/               # 🔧 Скрипты управления
└── Spec/                  # Спецификации и дизайн
```

---

## 🔄 Changelog

### Version 1.0.1 (26.10.2025)
- ✅ Добавлена поддержка кириллицы в PDF
- ✅ Исправлены права доступа к БД в Docker
- ✅ Настроен SSH доступ без паролей
- ✅ Созданы скрипты управления сервером

### Version 1.0.0 (26.10.2025)
- 🎉 Первый релиз
- ✅ Полный функционал MVP
- ✅ Интеграция с OpenAI
- ✅ Docker поддержка
- ✅ Автоматическое тестирование

Полный журнал изменений: [`docs/CHANGELOG_MOCK_TRANSCRIPTION.md`](docs/CHANGELOG_MOCK_TRANSCRIPTION.md)

---

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста:

1. Форкните репозиторий
2. Создайте ветку для вашей функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

---

## 📝 Лицензия

MIT License — см. файл [LICENSE](LICENSE) для деталей.

---

## 💬 Поддержка

- 📧 Email: support@elia-platform.ru
- 💬 Telegram: @elia_support
- 📖 Документация: [`docs/`](docs/)
- 🐛 Баг-репорты: [GitHub Issues](https://github.com/your-repo/issues)

---

## 🙏 Благодарности

Проект создан для упрощения работы врачей и улучшения качества медицинского обслуживания.

**Сделано с ❤️ для врачей**

---

## 🔗 Полезные ссылки

- [Быстрый старт](docs/QUICKSTART.md)
- [Настройка OpenAI](docs/OPENAI_SETUP.md)
- [Docker руководство](docs/DOCKER_GUIDE.md)
- [Развёртывание на Ubuntu](docs/UBUNTU_DEPLOYMENT.md)
- [Управление сервером](scripts/README.md)
- [SSH настройка](docs/SSH_SETUP.md)
- [Шпаргалки](docs/cheatsheets/) — быстрые справочники по командам
