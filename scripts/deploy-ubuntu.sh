#!/bin/bash
# Скрипт автоматического развертывания Elia Platform на Ubuntu сервере

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Проверка прав root
if [[ $EUID -eq 0 ]]; then
   error "Этот скрипт не должен запускаться от root. Запустите от обычного пользователя с sudo правами."
fi

# Переменные
PROJECT_DIR="/opt/elia-platform"
DOMAIN=""
OPENAI_KEY=""
EMAIL=""
INSTALL_NGINX=true
INSTALL_SSL=true

# Функция помощи
show_help() {
    echo "Использование: $0 [опции]"
    echo ""
    echo "Опции:"
    echo "  -d, --domain DOMAIN     Домен для приложения (обязательно)"
    echo "  -k, --openai-key KEY   OpenAI API ключ (обязательно)"
    echo "  -e, --email EMAIL      Email для SSL сертификата"
    echo "  --no-nginx             Не устанавливать Nginx"
    echo "  --no-ssl               Не настраивать SSL"
    echo "  -h, --help             Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 -d elia.su -k sk-... -e admin@elia.su"
    echo "  $0 --domain elia.su --openai-key sk-... --email admin@elia.su"
}

# Парсинг аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -k|--openai-key)
            OPENAI_KEY="$2"
            shift 2
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        --no-nginx)
            INSTALL_NGINX=false
            shift
            ;;
        --no-ssl)
            INSTALL_SSL=false
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            error "Неизвестный параметр: $1"
            ;;
    esac
done

# Проверка обязательных параметров
if [[ -z "$DOMAIN" ]]; then
    error "Домен обязателен. Используйте -d или --domain"
fi

if [[ -z "$OPENAI_KEY" ]]; then
    error "OpenAI API ключ обязателен. Используйте -k или --openai-key"
fi

if [[ "$INSTALL_SSL" == true && -z "$EMAIL" ]]; then
    warn "Email не указан. SSL сертификат не будет настроен."
    INSTALL_SSL=false
fi

log "Начинаем развертывание Elia Platform на Ubuntu сервере"
log "Домен: $DOMAIN"
log "OpenAI ключ: ${OPENAI_KEY:0:10}..."
log "Установка Nginx: $INSTALL_NGINX"
log "Установка SSL: $INSTALL_SSL"

# Обновление системы
log "Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
log "Установка необходимых пакетов..."
sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Установка Docker
log "Установка Docker..."
if ! command -v docker &> /dev/null; then
    # Удаление старых версий
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Добавление официального GPG ключа Docker
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Добавление репозитория Docker
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Установка Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Добавление пользователя в группу docker
    sudo usermod -aG docker $USER
    
    # Включение автозапуска Docker
    sudo systemctl enable docker
    sudo systemctl start docker
    
    log "Docker установлен успешно"
else
    log "Docker уже установлен"
fi

# Проверка Docker Compose
if ! docker compose version &> /dev/null; then
    log "Установка Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    log "Docker Compose уже установлен"
fi

# Создание директории проекта
log "Создание директории проекта..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
cd $PROJECT_DIR

# Клонирование репозитория проекта
log "Клонирование репозитория проекта..."
if [[ -d "../Elia" ]]; then
    # Если репозиторий уже склонирован локально
    cp -r ../Elia/* .
    cp -r ../Elia/.* . 2>/dev/null || true
else
    # Клонирование с GitHub
    git clone https://github.com/AlexeyKorzhebin/Elia.git temp-repo
    cp -r temp-repo/* .
    cp -r temp-repo/.* . 2>/dev/null || true
    rm -rf temp-repo
fi

# Проверяем, что файлы скопированы
if [[ ! -f "docker-compose.yml" ]]; then
    log "Создание базовых файлов..."
    mkdir -p app static templates data logs
    cat > docker-compose.yml << 'EOF'
services:
  elia-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: elia-platform
    ports:
      - "${PORT:-80}:80"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./static/uploads:/app/static/uploads
      - ./logs:/app/logs
      - ./.env:/app/.env:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
EOF

    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY app ./app
COPY static ./static
COPY templates ./templates

# Создание необходимых директорий
RUN mkdir -p static/uploads data logs

# Открытие порта
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Запуск приложения
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

    cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic-settings==2.0.3
sqlalchemy==2.0.23
aiosqlite==0.19.0
python-multipart==0.0.6
jinja2==3.1.2
aiofiles==23.2.1
openai==1.3.0
python-dotenv==1.0.0
EOF
fi

# Создание .env файла
log "Создание конфигурации..."
if [[ -f ".env.example" ]]; then
    # Используем существующий .env.example как основу
    cp .env.example .env
    log "Скопирован .env.example в .env"
else
    # Создаем .env с базовыми настройками
    cat > .env << EOF
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

# OpenAI API (замените на ваш ключ!)
OPENAI_API_KEY=$OPENAI_KEY
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# Дополнительные настройки для продакшн
PYTHONPATH=/app
PYTHONUNBUFFERED=1

# Безопасность
SECRET_KEY=$(openssl rand -hex 32)

# Домен
DOMAIN=$DOMAIN
EOF
fi

# Обновляем параметры в .env файле
log "Обновление параметров в .env..."
sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_KEY|g" .env
sed -i "s|DOMAIN=.*|DOMAIN=$DOMAIN|g" .env
sed -i "s|DEBUG=.*|DEBUG=false|g" .env
sed -i "s|LOG_LEVEL=.*|LOG_LEVEL=INFO|g" .env

# Создание необходимых директорий
log "Создание директорий..."
mkdir -p data logs static/uploads
chmod -R 755 data logs static/uploads

# Проверяем наличие файлов приложения
if [[ ! -f "app/main.py" ]]; then
    log "Создание базовых файлов приложения (заглушки)..."
    mkdir -p app/api app/models app/schemas app/services templates

    cat > app/__init__.py << 'EOF'
# Elia Platform
EOF

    cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

app = FastAPI(title="Elia AI Platform", version="1.0.0")

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Шаблоны
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

    cat > app/config.py << 'EOF'
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    database_url: str = "sqlite+aiosqlite:///./elia.db"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    upload_dir: str = "static/uploads"
    max_upload_size: int = 52428800
    app_name: str = "Elia AI Platform"
    version: str = "1.0.0"
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_retention_days: int = 30
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4"
    secret_key: str = ""
    domain: str = ""

settings = Settings()
EOF

    cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elia AI Platform</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Elia AI Platform</h1>
        <p class="status">✅ Приложение успешно развернуто!</p>
        <p>Домен: {{ request.url.hostname }}</p>
        <p>Версия: 1.0.0</p>
        <p>Статус: <span class="status">Работает</span></p>
    </div>
</body>
</html>
EOF
else
    log "Файлы приложения уже существуют, пропускаем создание заглушек"
fi

# Использование образа из Docker Hub
log "Использование образа из Docker Hub..."
log "Образ: alexeykorzhebin/elia-platform:latest"

# Обновляем docker-compose.yml для использования образа из Docker Hub
log "Обновление docker-compose.yml для использования образа из Docker Hub..."
cat > docker-compose.yml << 'EOF'
services:
  elia-app:
    image: alekseykorzhebin/elia-platform:latest
    container_name: elia-platform
    ports:
      - "127.0.0.1:8000:80"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./static/uploads:/app/static/uploads
      - ./logs:/app/logs
      - ./elia.db:/app/elia.db
      - ./.env:/app/.env:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
EOF

# Установка Nginx
if [[ "$INSTALL_NGINX" == true ]]; then
    log "Установка Nginx..."
    sudo apt install -y nginx
    
    # Создание конфигурации Nginx
    log "Настройка Nginx..."
    sudo tee /etc/nginx/sites-available/elia-platform > /dev/null << EOF
server {
    server_name $DOMAIN;
    
    # Логи
    access_log /var/log/nginx/elia-access.log;
    error_log /var/log/nginx/elia-error.log;
    
    # Максимальный размер загружаемых файлов
    client_max_body_size 50M;
    
    # Проксирование на Docker контейнер (порт 8000)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    listen 80;
}
EOF

    # Активация конфигурации
    sudo ln -sf /etc/nginx/sites-available/elia-platform /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Проверка конфигурации
    sudo nginx -t
    
    # Запуск Nginx
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    
    log "Nginx настроен и запущен"
fi

# Настройка SSL
if [[ "$INSTALL_SSL" == true ]]; then
    log "Настройка SSL сертификата..."
    sudo apt install -y certbot python3-certbot-nginx
    
    # Останавливаем контейнер временно для получения сертификата
    log "Временная остановка контейнера для получения SSL сертификата..."
    sudo systemctl stop elia-platform 2>/dev/null || true
    
    # Получение сертификата с автоматическим редиректом
    sudo certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive --redirect
    
    # Автоматическое обновление настроено через certbot.timer
    log "Автоматическое обновление сертификата настроено через systemd timer"
    
    # Запускаем контейнер обратно
    log "Запуск контейнера после получения SSL сертификата..."
    sudo systemctl start elia-platform
    
    log "SSL сертификат настроен"
fi

# Создание systemd сервиса
log "Создание systemd сервиса..."
sudo tee /etc/systemd/system/elia-platform.service > /dev/null << EOF
[Unit]
Description=Elia AI Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
ExecReload=/usr/bin/docker compose restart
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Активация сервиса
sudo systemctl daemon-reload
sudo systemctl enable elia-platform

# Загрузка и запуск приложения
log "Загрузка образа из Docker Hub..."
docker pull alekseykorzhebin/elia-platform:latest

log "Запуск приложения..."
sudo systemctl start elia-platform

# Ожидание запуска
log "Ожидание запуска приложения..."
sleep 10

# Проверка статуса
if sudo systemctl is-active --quiet elia-platform; then
    log "Приложение успешно запущено!"
else
    error "Ошибка запуска приложения. Проверьте логи: sudo journalctl -u elia-platform"
fi

# Настройка файрвола
log "Настройка файрвола..."
sudo apt install -y ufw
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Создание скрипта бэкапа
log "Создание скрипта бэкапа..."
sudo tee /opt/elia-platform/backup.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/elia-platform"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап базы данных
if [[ -f /opt/elia-platform/data/elia.db ]]; then
    cp /opt/elia-platform/data/elia.db $BACKUP_DIR/elia_$DATE.db
fi

# Бэкап загруженных файлов
if [[ -d /opt/elia-platform/static/uploads ]]; then
    tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /opt/elia-platform static/uploads/
fi

# Бэкап конфигурации
cp /opt/elia-platform/.env $BACKUP_DIR/env_$DATE

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "env_*" -mtime +30 -delete

echo "Бэкап завершен: $DATE"
EOF

sudo chmod +x /opt/elia-platform/backup.sh

# Настройка ежедневного бэкапа
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/elia-platform/backup.sh") | crontab -

# Финальная проверка
log "Выполнение финальной проверки..."

# Проверка статуса сервисов
if sudo systemctl is-active --quiet elia-platform; then
    log "✅ Elia Platform: работает"
else
    warn "❌ Elia Platform: не работает"
fi

if [[ "$INSTALL_NGINX" == true ]]; then
    if sudo systemctl is-active --quiet nginx; then
        log "✅ Nginx: работает"
    else
        warn "❌ Nginx: не работает"
    fi
fi

if sudo systemctl is-active --quiet docker; then
    log "✅ Docker: работает"
else
    warn "❌ Docker: не работает"
fi

# Проверка доступности
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health | grep -q "200"; then
    log "✅ Приложение отвечает на health check (порт 8000)"
else
    warn "❌ Приложение не отвечает на health check"
fi

if [[ "$INSTALL_NGINX" == true ]]; then
    PROTOCOL="http"
    if [[ "$INSTALL_SSL" == true ]]; then
        PROTOCOL="https"
    fi
    if curl -s -o /dev/null -w "%{http_code}" $PROTOCOL://$DOMAIN/health | grep -q "200"; then
        log "✅ Сайт доступен через Nginx ($PROTOCOL://$DOMAIN)"
    else
        warn "❌ Сайт недоступен через Nginx"
    fi
fi

# Итоговая информация
log "🎉 Развертывание завершено!"
echo ""
echo "📋 Информация о развертывании:"
echo "  Домен: $DOMAIN"
echo "  Проект: $PROJECT_DIR"
echo "  Статус: $(sudo systemctl is-active elia-platform)"
echo ""
echo "🔧 Полезные команды:"
echo "  sudo systemctl status elia-platform    # Статус приложения"
echo "  sudo systemctl restart elia-platform   # Перезапуск"
echo "  docker compose logs -f                 # Логи приложения"
echo "  sudo journalctl -u elia-platform -f   # Логи systemd"
echo "  /opt/elia-platform/backup.sh          # Ручной бэкап"
echo ""
echo "🌐 Доступ к приложению:"
if [[ "$INSTALL_SSL" == true ]]; then
    echo "  https://$DOMAIN"
    echo "  https://$DOMAIN/health (health check)"
else
    echo "  http://$DOMAIN"
    echo "  http://$DOMAIN/health (health check)"
fi
echo ""
echo "📚 Документация:"
echo "  /opt/elia-platform/UBUNTU_DEPLOYMENT.md"
echo ""
echo "⚠️  ВАЖНО:"
echo "  - Проверьте работу приложения: curl http://$DOMAIN/health"
echo "  - Настройте мониторинг и алерты"
echo "  - Регулярно обновляйте систему: sudo apt update && sudo apt upgrade"
echo "  - Делайте бэкапы: /opt/elia-platform/backup.sh"

log "Развертывание успешно завершено! 🚀"
