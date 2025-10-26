# 🐳 Elia Platform в Docker Hub - Инструкция по использованию

## ✅ Образ собран и готов к публикации

**Образ:** `alexeykorzhebin/elia-platform`
**Теги:** `1.0.0`, `latest`
**Размер:** ~200MB (оптимизированный multi-stage build)

---

## 🚀 Как использовать образ из Docker Hub

### Способ 1: Через docker-compose (рекомендуется)

```bash
# Используйте готовый docker-compose.hub.yml
docker-compose -f docker-compose.hub.yml up -d
```

### Способ 2: Прямое использование Docker

```bash
# Создайте .env файл
cat > .env << 'EOF'
DATABASE_URL=sqlite+aiosqlite:///./data/elia.db
HOST=0.0.0.0
PORT=8000
DEBUG=false
OPENAI_API_KEY=ваш-ключ-openai
OPENAI_MODEL=gpt-4
EOF

# Создайте директории
mkdir -p data logs static/uploads

# Запустите контейнер
docker run -d \
  --name elia-platform \
  -p 80:80 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/static/uploads:/app/static/uploads \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  alexeykorzhebin/elia-platform:latest
```

### Способ 3: Обновленный скрипт развертывания

```bash
# Скрипт автоматически использует образ из Docker Hub
./deploy-ubuntu.sh -d elia.su -k ваш-ключ -e admin@elia.su
```

---

## 📋 Преимущества использования Docker Hub

### ✅ Быстрое развертывание
- Не нужно собирать образ на сервере
- Готовый оптимизированный образ
- Быстрая загрузка и запуск

### ✅ Стабильность
- Образ протестирован и готов к продакшн
- Все зависимости предустановлены
- Безопасность (запуск от непривилегированного пользователя)

### ✅ Версионирование
- Тег `latest` - последняя версия
- Тег `1.0.0` - конкретная версия
- Легкое обновление и откат

---

## 🔧 Обновление скрипта развертывания

Скрипт `deploy-ubuntu.sh` теперь использует образ из Docker Hub вместо сборки:

```bash
# Вместо сборки образа:
# docker compose build

# Используется готовый образ:
# image: alexeykorzhebin/elia-platform:latest
```

---

## 📊 Структура образа

```
alexeykorzhebin/elia-platform:latest
├── Python 3.11-slim (базовый образ)
├── Все зависимости из requirements.txt
├── Код приложения (/app)
├── Статические файлы (/app/static)
├── HTML шаблоны (/app/templates)
├── Непривилегированный пользователь (elia)
├── Health check настроен
└── Оптимизированный размер (~200MB)
```

---

## 🛡️ Безопасность образа

- ✅ **Непривилегированный пользователь** - запуск от `elia:elia`
- ✅ **Минимальный базовый образ** - Python 3.11-slim
- ✅ **Только необходимые пакеты** - оптимизированные зависимости
- ✅ **Health check** - мониторинг состояния
- ✅ **Multi-stage build** - минимизация размера

---

## 🔄 Обновление приложения

### Обновление образа:

```bash
# Получить новую версию
docker pull alexeykorzhebin/elia-platform:latest

# Перезапустить контейнер
docker-compose -f docker-compose.hub.yml down
docker-compose -f docker-compose.hub.yml up -d
```

### Обновление через скрипт:

```bash
# Скрипт автоматически использует последнюю версию
./deploy-ubuntu.sh -d elia.su -k ваш-ключ -e admin@elia.su
```

---

## 📚 Файлы для использования Docker Hub

### 1. `docker-compose.hub.yml`
```yaml
services:
  elia-app:
    image: alexeykorzhebin/elia-platform:latest
    # ... остальная конфигурация
```

### 2. Обновленный `deploy-ubuntu.sh`
- Использует образ из Docker Hub
- Не собирает образ локально
- Быстрое развертывание

### 3. `Dockerfile.production`
- Оптимизированный для продакшн
- Multi-stage build
- Безопасность

---

## 🎯 Команды для публикации в Docker Hub

### Вход в Docker Hub:
```bash
docker login
# Введите username: alexeykorzhebin
# Введите password: [ваш пароль]
```

### Загрузка образа:
```bash
# Загрузить тег latest
docker push alexeykorzhebin/elia-platform:latest

# Загрузить тег версии
docker push alexeykorzhebin/elia-platform:1.0.0
```

### Автоматическая загрузка через скрипт:
```bash
./scripts/build-and-push.sh --push
```

---

## ✅ Проверка работы образа

### Локальная проверка:
```bash
# Запустить контейнер
docker run -d --name elia-test -p 80:80 alexeykorzhebin/elia-platform:latest

# Проверить health check
curl http://localhost:80/health

# Проверить логи
docker logs elia-test

# Остановить тестовый контейнер
docker stop elia-test && docker rm elia-test
```

### Проверка на сервере:
```bash
# После развертывания
curl https://elia.su/health
# Ожидается: {"status":"healthy"}
```

---

## 📖 Документация

- **`docker-compose.hub.yml`** - конфигурация для Docker Hub
- **`Dockerfile.production`** - продакшн Dockerfile
- **`scripts/build-and-push.sh`** - скрипт сборки и публикации
- **`.dockerignore`** - исключения для сборки

---

## 🎉 Готово!

**Elia Platform готов к использованию через Docker Hub!**

- ✅ Образ собран и оптимизирован
- ✅ Скрипт развертывания обновлен
- ✅ Конфигурация для Docker Hub готова
- ✅ Инструкции по использованию созданы

**Для публикации в Docker Hub выполните:**
```bash
docker login
./scripts/build-and-push.sh --push
```

**Для развертывания на сервере:**
```bash
./deploy-ubuntu.sh -d elia.su -k ваш-ключ -e admin@elia.su
```

---

**Elia Platform теперь доступен через Docker Hub! 🚀**
