#!/bin/bash
# Скрипт мониторинга ресурсов на удаленном сервере

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SERVER="root@43.245.224.114"
CONTAINER="elia-platform"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}           МОНИТОРИНГ РЕСУРСОВ ELIA PLATFORM              ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Информация о контейнере
echo -e "${BLUE}📦 Docker контейнер:${NC}"
ssh $SERVER "docker stats $CONTAINER --no-stream --format 'CPU: {{.CPUPerc}}  |  Память: {{.MemUsage}} ({{.MemPerc}})  |  Сеть: {{.NetIO}}  |  Диск I/O: {{.BlockIO}}'"
echo ""

# Процесс внутри контейнера
echo -e "${BLUE}⚙️  Основной процесс:${NC}"
ssh $SERVER "docker top $CONTAINER | tail -n 1 | awk '{print \"PID: \"\$2\"  |  CPU: \"\$3\"%  |  Memory: \"\$4\" (RSS: \"\$5\" KB)  |  Command: \"\$8\" \"\$9\" \"\$10}'"
echo ""

# Память системы
echo -e "${BLUE}💾 Память системы:${NC}"
ssh $SERVER "free -h | grep Mem | awk '{print \"Всего: \"\$2\"  |  Используется: \"\$3\"  |  Свободно: \"\$4\"  |  Доступно: \"\$7}'"
MEMORY_PERCENT=$(ssh $SERVER "free | grep Mem | awk '{printf \"%.1f\", \$3/\$2 * 100}'")
if (( $(echo "$MEMORY_PERCENT > 80" | bc -l) )); then
    echo -e "${RED}⚠️  Использование памяти: ${MEMORY_PERCENT}%${NC}"
elif (( $(echo "$MEMORY_PERCENT > 60" | bc -l) )); then
    echo -e "${YELLOW}⚠️  Использование памяти: ${MEMORY_PERCENT}%${NC}"
else
    echo -e "${GREEN}✓ Использование памяти: ${MEMORY_PERCENT}%${NC}"
fi
echo ""

# Диск
echo -e "${BLUE}💿 Использование диска:${NC}"
ssh $SERVER "df -h / | tail -n 1 | awk '{print \"Раздел: \"\$1\"  |  Размер: \"\$2\"  |  Использовано: \"\$3\"  |  Свободно: \"\$4\"  |  Процент: \"\$5}'"
DISK_PERCENT=$(ssh $SERVER "df / | tail -n 1 | awk '{print \$5}' | sed 's/%//'")
if [ "$DISK_PERCENT" -gt 80 ]; then
    echo -e "${RED}⚠️  Диск заполнен на ${DISK_PERCENT}%${NC}"
elif [ "$DISK_PERCENT" -gt 60 ]; then
    echo -e "${YELLOW}⚠️  Диск заполнен на ${DISK_PERCENT}%${NC}"
else
    echo -e "${GREEN}✓ Диск заполнен на ${DISK_PERCENT}%${NC}"
fi
echo ""

# База данных
echo -e "${BLUE}🗄️  База данных:${NC}"
DB_SIZE=$(ssh $SERVER "du -h /opt/elia-platform/elia.db 2>/dev/null | cut -f1" || echo "N/A")
echo -e "Размер БД: ${DB_SIZE}"
echo ""

# Загрузка системы
echo -e "${BLUE}📊 Загрузка системы:${NC}"
ssh $SERVER "uptime | awk -F'load average:' '{print \"Load Average (1m, 5m, 15m): \"\$2}'"
echo ""

# CPU
echo -e "${BLUE}⚡ CPU:${NC}"
CPU_CORES=$(ssh $SERVER "nproc")
echo "Количество ядер: $CPU_CORES"
ssh $SERVER "top -bn1 | grep 'Cpu(s)' | awk '{print \"Использование: \"\$2\" user, \"\$4\" system, \"\$8\" idle\"}'"
echo ""

# Сетевая активность
echo -e "${BLUE}🌐 Сетевая активность:${NC}"
ssh $SERVER "docker stats $CONTAINER --no-stream --format 'Получено: {{.NetIO}}' | awk -F' / ' '{print \"Входящий: \"\$1\"  |  Исходящий: \"\$2}'"
echo ""

# Uptime
echo -e "${BLUE}⏱️  Время работы:${NC}"
ssh $SERVER "uptime -p"
echo ""

# Systemd сервис
echo -e "${BLUE}🔧 Systemd сервис:${NC}"
ssh $SERVER "systemctl show elia-platform --property=MemoryCurrent,CPUUsageNSec,TasksCurrent | 
    while IFS='=' read key value; do
        case \$key in
            MemoryCurrent) echo \"Память: \$(numfmt --to=iec \$value 2>/dev/null || echo \$value)\" ;;
            CPUUsageNSec) echo \"CPU время: \$(echo \"\$value / 1000000000\" | bc)s\" ;;
            TasksCurrent) echo \"Задачи: \$value\" ;;
        esac
    done"
echo ""

# Проверка здоровья
echo -e "${BLUE}❤️  Здоровье приложения:${NC}"
HEALTH=$(ssh $SERVER "curl -sf http://localhost/health" 2>/dev/null || echo "error")
if [ "$HEALTH" != "error" ]; then
    echo -e "${GREEN}✓ Приложение работает нормально${NC}"
    echo "$HEALTH" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Статус: {data['status']}  |  Версия: {data['version']}\")" 2>/dev/null || echo "$HEALTH"
else
    echo -e "${RED}✗ Приложение не отвечает${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

