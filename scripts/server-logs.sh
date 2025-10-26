#!/bin/bash
# Скрипт для просмотра логов на удаленном сервере

set -e

SERVER="root@43.245.224.114"
LINES="${1:-100}"  # По умолчанию 100 строк

echo "=== Логи Elia Platform (последние $LINES строк) ==="
echo ""

ssh $SERVER "docker logs elia-platform --tail=$LINES --follow"

