#!/bin/bash
# Скрипт для сборки и публикации Elia Platform в Docker Hub

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
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

# Переменные
DOCKER_USERNAME="alekseykorzhebin"
IMAGE_NAME="elia-platform"
VERSION="1.0.0"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}"
BUILD_ARGS=""
PLATFORMS="linux/amd64,linux/arm64"  # Поддержка обеих архитектур
USE_BUILDX=true  # Использовать buildx для multi-platform сборки

# Функция помощи
show_help() {
    echo "Использование: $0 [опции]"
    echo ""
    echo "Опции:"
    echo "  -u, --username USERNAME   Docker Hub username (по умолчанию: alekseykorzhebin)"
    echo "  -n, --name NAME          Имя образа (по умолчанию: elia-platform)"
    echo "  -v, --version VERSION   Версия образа (по умолчанию: 1.0.0)"
    echo "  -t, --tag TAG            Дополнительный тег"
    echo "  --platform PLATFORMS     Платформы для сборки (по умолчанию: linux/amd64,linux/arm64)"
    echo "  --no-buildx              Использовать обычный docker build вместо buildx"
    echo "  --no-cache               Сборка без кэша"
    echo "  --push                   Загрузить в Docker Hub"
    echo "  --login                  Войти в Docker Hub"
    echo "  -h, --help               Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 --push                                    # Собрать и загрузить"
    echo "  $0 --no-cache --push                        # Собрать без кэша и загрузить"
    echo "  $0 -v 1.1.0 -t latest --push                # Собрать версию 1.1.0 с тегом latest"
    echo "  $0 --login                                   # Только войти в Docker Hub"
}

# Парсинг аргументов
PUSH=false
LOGIN=false
NO_CACHE=""
TAGS=()
NO_BUILDX=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--username)
            DOCKER_USERNAME="$2"
            FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}"
            shift 2
            ;;
        -n|--name)
            IMAGE_NAME="$2"
            FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -t|--tag)
            TAGS+=("$2")
            shift 2
            ;;
        --platform)
            PLATFORMS="$2"
            shift 2
            ;;
        --no-buildx)
            NO_BUILDX=true
            USE_BUILDX=false
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --login)
            LOGIN=true
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

log "🐳 Сборка и публикация Elia Platform в Docker Hub"
log "Образ: ${FULL_IMAGE_NAME}"
log "Версия: ${VERSION}"

# Проверка Docker
if ! command -v docker &> /dev/null; then
    error "Docker не установлен. Установите Docker и повторите попытку."
fi

# Проверка авторизации в Docker Hub
if [[ "$PUSH" == true ]]; then
    if ! docker info | grep -q "Username:"; then
        warn "Не авторизован в Docker Hub. Выполняю вход..."
        docker login
    fi
fi

# Если только вход
if [[ "$LOGIN" == true ]]; then
    log "Вход в Docker Hub..."
    docker login
    log "Вход выполнен успешно!"
    exit 0
fi

# Проверка файлов
if [[ ! -f "Dockerfile.production" ]]; then
    error "Файл Dockerfile.production не найден"
fi

if [[ ! -f "requirements.txt" ]]; then
    error "Файл requirements.txt не найден"
fi

if [[ ! -d "app" ]]; then
    error "Директория app не найдена"
fi

# Создание тегов
TAGS+=("${VERSION}")
if [[ "$VERSION" != "latest" ]]; then
    TAGS+=("latest")
fi

# Проверка и настройка buildx для multi-platform сборки
if [[ "$USE_BUILDX" == true && "$PUSH" == true ]]; then
    log "Настройка Docker buildx для multi-platform сборки..."
    
    # Создаём builder если его нет
    if ! docker buildx ls | grep -q "multiplatform-builder"; then
        log "Создание buildx builder..."
        docker buildx create --name multiplatform-builder --use --bootstrap 2>/dev/null || true
    else
        log "Использование существующего buildx builder..."
        docker buildx use multiplatform-builder 2>/dev/null || true
    fi
    
    log "Сборка Docker образа для платформ: ${PLATFORMS}..."
    BUILD_CMD="docker buildx build --platform ${PLATFORMS} -f Dockerfile.production ${NO_CACHE}"
    
    # Добавляем теги
    for tag in "${TAGS[@]}"; do
        BUILD_CMD="${BUILD_CMD} -t ${FULL_IMAGE_NAME}:${tag}"
    done
    
    # Для buildx с push нужно указать --push
    if [[ "$PUSH" == true ]]; then
        BUILD_CMD="${BUILD_CMD} --push"
    fi
    
    BUILD_CMD="${BUILD_CMD} ."
    
    log "Выполняю: ${BUILD_CMD}"
    eval $BUILD_CMD
    
    if [[ $? -eq 0 ]]; then
        log "✅ Образ успешно собран для всех платформ!"
    else
        error "❌ Ошибка сборки образа"
    fi
else
    # Обычная сборка (локальная или без buildx)
    log "Сборка Docker образа..."
    BUILD_CMD="docker build -f Dockerfile.production ${NO_CACHE}"
    
    # Добавляем теги
    for tag in "${TAGS[@]}"; do
        BUILD_CMD="${BUILD_CMD} -t ${FULL_IMAGE_NAME}:${tag}"
    done
    
    BUILD_CMD="${BUILD_CMD} ."
    
    log "Выполняю: ${BUILD_CMD}"
    eval $BUILD_CMD
    
    if [[ $? -eq 0 ]]; then
        log "✅ Образ успешно собран!"
    else
        error "❌ Ошибка сборки образа"
    fi
fi

# Показываем информацию об образе (только если не использовали buildx с push)
if [[ "$USE_BUILDX" != true || "$PUSH" != true ]]; then
    log "Информация об образе:"
    docker images | grep "${FULL_IMAGE_NAME}"
fi

# Загрузка в Docker Hub (только если не использовали buildx с --push)
if [[ "$PUSH" == true && "$USE_BUILDX" != true ]]; then
    log "Загрузка образа в Docker Hub..."
    
    for tag in "${TAGS[@]}"; do
        log "Загружаю тег: ${FULL_IMAGE_NAME}:${tag}"
        docker push "${FULL_IMAGE_NAME}:${tag}"
        
        if [[ $? -eq 0 ]]; then
            log "✅ Тег ${tag} успешно загружен!"
        else
            error "❌ Ошибка загрузки тега ${tag}"
        fi
    done
    
    log "🎉 Все теги успешно загружены в Docker Hub!"
    log "Образ доступен по адресу: https://hub.docker.com/r/${FULL_IMAGE_NAME}"
elif [[ "$PUSH" == true && "$USE_BUILDX" == true ]]; then
    log "🎉 Образ успешно собран и загружен в Docker Hub для всех платформ!"
    log "Образ доступен по адресу: https://hub.docker.com/r/${FULL_IMAGE_NAME}"
    log "Поддерживаемые платформы: ${PLATFORMS}"
else
    log "Образ собран локально. Для загрузки в Docker Hub используйте --push"
fi

# Создание docker-compose.yml для использования образа
log "Создание docker-compose.yml для использования образа из Docker Hub..."
cat > docker-compose.hub.yml << EOF
services:
  elia-app:
    image: ${FULL_IMAGE_NAME}:${VERSION}
    container_name: elia-platform
    ports:
      - "\${PORT:-8000}:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./static/uploads:/app/static/uploads
      - ./logs:/app/logs
      - ./.env:/app/.env:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
EOF

log "✅ Создан файл docker-compose.hub.yml для использования образа из Docker Hub"

# Инструкции по использованию
echo ""
log "📋 Инструкции по использованию:"
echo ""
echo "1. Использование образа из Docker Hub:"
echo "   docker-compose -f docker-compose.hub.yml up -d"
echo ""
echo "2. Прямое использование образа:"
echo "   docker run -d \\"
echo "     --name elia-platform \\"
echo "     -p 8000:8000 \\"
echo "     -v \$(pwd)/data:/app/data \\"
echo "     -v \$(pwd)/static/uploads:/app/static/uploads \\"
echo "     -v \$(pwd)/logs:/app/logs \\"
echo "     --env-file .env \\"
echo "     ${FULL_IMAGE_NAME}:${VERSION}"
echo ""
echo "3. Обновление образа:"
echo "   docker pull ${FULL_IMAGE_NAME}:${VERSION}"
echo "   docker-compose -f docker-compose.hub.yml up -d"
echo ""

if [[ "$PUSH" == true ]]; then
    echo "4. Проверка в Docker Hub:"
    echo "   https://hub.docker.com/r/${FULL_IMAGE_NAME}"
    echo ""
fi

log "🎉 Готово! Elia Platform готов к использованию!"
