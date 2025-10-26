# 🚀 Обновленный скрипт deploy-ubuntu.sh для Elia Platform

## ✅ Что было исправлено:

1. ✅ **Репозиторий обновлен** - теперь используется `https://github.com/AlexeyKorzhebin/Elia`
2. ✅ **Домен по умолчанию** - `elia.su`
3. ✅ **Умное использование .env** - скрипт использует существующий `.env.example` если есть
4. ✅ **Проверка файлов** - не создает заглушки если файлы уже существуют

---

## 🎯 Использование обновленного скрипта

### Основная команда для elia.su:

```bash
./deploy-ubuntu.sh -d elia.su -k ваш-openai-ключ -e admin@elia.su
```

### Примеры с разными параметрами:

```bash
# Полная установка с SSL
./deploy-ubuntu.sh -d elia.su -k sk-proj-abc123... -e admin@elia.su

# Установка без SSL (для тестирования)
./deploy-ubuntu.sh -d elia.su -k sk-proj-abc123... --no-ssl

# Установка без Nginx (если уже есть)
./deploy-ubuntu.sh -d elia.su -k sk-proj-abc123... -e admin@elia.su --no-nginx

# Минимальная установка
./deploy-ubuntu.sh -d elia.su -k sk-proj-abc123... --no-nginx --no-ssl
```

---

## 🔧 Как работает обновленный скрипт

### 1. Клонирование репозитория
```bash
# Скрипт автоматически клонирует:
git clone https://github.com/AlexeyKorzhebin/Elia.git
```

### 2. Умное создание .env
```bash
# Если есть .env.example - использует его как основу
if [[ -f ".env.example" ]]; then
    cp .env.example .env
else
    # Создает базовый .env
fi

# Обновляет параметры из командной строки
sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_KEY|g" .env
sed -i "s|DOMAIN=.*|DOMAIN=$DOMAIN|g" .env
```

### 3. Проверка файлов приложения
```bash
# Не создает заглушки если файлы уже есть
if [[ ! -f "app/main.py" ]]; then
    # Создает только если файлов нет
fi
```

---

## 📋 Параметры скрипта

### Обязательные:
- **`-d elia.su`** - домен приложения
- **`-k sk-...`** - OpenAI API ключ

### Опциональные:
- **`-e admin@elia.su`** - email для SSL сертификата
- **`--no-nginx`** - не устанавливать Nginx
- **`--no-ssl`** - не настраивать SSL

---

## 🌐 Настройка домена elia.su

### 1. Настройте DNS записи:
```
Тип: A
Имя: @
Значение: IP_ВАШЕГО_СЕРВЕРА
TTL: 3600
```

### 2. Проверьте настройку:
```bash
nslookup elia.su
# Должен вернуть IP вашего сервера
```

---

## 🔑 Получение OpenAI API ключа

1. Зайдите на https://platform.openai.com/
2. Войдите в аккаунт
3. Перейдите в API Keys: https://platform.openai.com/api-keys
4. Создайте новый ключ (начинается с `sk-`)
5. Пополните баланс (минимум $5)

---

## 🚀 Быстрый старт

### На Ubuntu сервере:

```bash
# 1. Подготовка
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git unzip

# 2. Скачивание скрипта
wget https://raw.githubusercontent.com/AlexeyKorzhebin/Elia/main/scripts/deploy-ubuntu.sh
chmod +x deploy-ubuntu.sh

# 3. Запуск установки
./deploy-ubuntu.sh -d elia.su -k ваш-openai-ключ -e admin@elia.su
```

---

## ✅ Что получится после установки

### Структура на сервере:
```
/opt/elia-platform/          # Проект из GitHub
├── .env                     # Конфигурация (из .env.example)
├── app/                     # Код приложения
├── static/                  # Статические файлы
├── templates/               # HTML шаблоны
├── data/elia.db             # База данных
├── logs/                    # Логи
└── static/uploads/          # Загрузки
```

### Сервисы:
- ✅ **Docker** - установлен и настроен
- ✅ **Elia Platform** - запущен в контейнере
- ✅ **Nginx** - настроен как reverse proxy
- ✅ **SSL** - сертификат от Let's Encrypt
- ✅ **Systemd** - автозапуск приложения
- ✅ **UFW** - файрвол настроен

---

## 🔧 Управление после установки

### Основные команды:
```bash
# Статус
sudo systemctl status elia-platform

# Перезапуск
sudo systemctl restart elia-platform

# Логи
sudo journalctl -u elia-platform -f
docker compose logs -f

# Обновление
cd /opt/elia-platform
git pull
docker compose build
sudo systemctl restart elia-platform
```

### Проверка работы:
```bash
# Health check
curl https://elia.su/health

# Открыть сайт
open https://elia.su
```

---

## 🐛 Устранение неполадок

### Проблема: Репозиторий не клонируется
```bash
# Проверьте доступность GitHub
ping github.com

# Проверьте права доступа
ls -la /opt/elia-platform
```

### Проблема: .env не создается
```bash
# Проверьте наличие .env.example
ls -la /opt/elia-platform/.env*

# Создайте вручную
cd /opt/elia-platform
cp .env.example .env
nano .env  # Отредактируйте параметры
```

### Проблема: SSL не работает
```bash
# Проверьте DNS
nslookup elia.su

# Проверьте сертификат
sudo certbot certificates

# Обновите сертификат
sudo certbot renew --dry-run
```

---

## 📚 Документация

- **`DEPLOY_PARAMETERS.md`** - подробное описание параметров
- **`deploy-parameters-cheatsheet.txt`** - шпаргалка команд
- **`UBUNTU_DEPLOYMENT.md`** - полное руководство по развертыванию

---

## 🎯 Итоговая команда для elia.su

```bash
./deploy-ubuntu.sh -d elia.su -k ваш-openai-ключ -e admin@elia.su
```

**Замените:**
- `ваш-openai-ключ` → ключ от OpenAI (начинается с `sk-`)
- `admin@elia.su` → ваш email

**Пример:**
```bash
./deploy-ubuntu.sh -d elia.su -k sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890 -e admin@elia.su
```

---

## ⚠️ Важные моменты

- ✅ Скрипт использует реальный репозиторий с GitHub
- ✅ Автоматически использует существующий `.env.example`
- ✅ Не создает заглушки если файлы уже есть
- ✅ Настроен для домена `elia.su`
- ✅ Все параметры можно изменить через `.env` после установки

---

**Готово! Скрипт обновлен для работы с вашим репозиторием! 🚀**
