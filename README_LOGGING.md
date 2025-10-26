# 📋 Система логирования Elia

## 🎯 Быстрый старт

### Настройка через .env

```env
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR=logs                # Директория для логов
LOG_RETENTION_DAYS=30       # Дней хранения логов
```

### Использование в коде

```python
from app.logger import get_logger

logger = get_logger(__name__)

logger.info("Информация о работе")
logger.warning("Предупреждение")
logger.error("Ошибка")
logger.exception("Исключение с stack trace")
```

## 📁 Структура логов

```
logs/
├── elia-app-2025-10-26.log       # 📝 Все логи
├── elia-errors-2025-10-26.log    # ❌ Только ошибки
└── elia-access-2025-10-26.log    # 🌐 HTTP запросы
```

## 🔍 Мониторинг

```bash
# В реальном времени
tail -f logs/elia-app-$(date +%Y-%m-%d).log

# Поиск ошибок
grep "ERROR" logs/elia-app-*.log

# Медленные запросы
grep "Медленный запрос" logs/elia-app-*.log
```

## ✅ Что работает

- ✅ Автоматическая ротация логов каждый день
- ✅ Файлы с датой в названии
- ✅ Автоудаление старых логов (30 дней)
- ✅ Цветная подсветка в консоли
- ✅ Отдельные файлы для ошибок
- ✅ HTTP access логи
- ✅ Stack trace для исключений
- ✅ Скрытие чувствительных данных
- ✅ Логирование во всех API endpoints

## 📚 Документация

- **[LOGGING_BEST_PRACTICES.md](./LOGGING_BEST_PRACTICES.md)** - Подробное руководство
- **[LOGGING_IMPLEMENTATION.md](./LOGGING_IMPLEMENTATION.md)** - Детали реализации

## 🧪 Тестирование

Протестировано ✅:
- Все уровни логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Запись в файлы
- Ротация по дням
- Цветной вывод в консоль
- Логирование исключений со stack trace
- HTTP middleware
- Разделение по типам (app/errors/access)

## 📊 Примеры логов

### Application Log
```
2025-10-26 17:38:36 - app.api.patients - INFO - get_patients_list:26 - Получено 15 пациентов
2025-10-26 17:38:40 - app.api.appointments - WARNING - get_patient_detail:43 - Пациент не найден: patient_id=999
```

### Error Log
```
2025-10-26 17:40:12 - app.api.appointments - ERROR - download_appointment_pdf:217 - Ошибка при генерации PDF
Traceback (most recent call last):
  File "app/api/appointments.py", line 194, in download_appointment_pdf
    pdf_buffer = generate_appointment_pdf(...)
ZeroDivisionError: division by zero
```

### Access Log
```
2025-10-26 17:38:36 - 127.0.0.1 - "GET /api/patients" 200 - 45.23ms
2025-10-26 17:38:40 - 127.0.0.1 - "GET /api/patients/999" 404 - 12.34ms
```

## 🎨 Цветная подсветка

В консоли логи выводятся с цветами:
- 🔹 **DEBUG** - серый
- 🔷 **INFO** - синий
- 🟡 **WARNING** - жёлтый
- 🔴 **ERROR** - красный
- 🔥 **CRITICAL** - ярко-красный

## ⚙️ Настройки производительности

### Development
```env
LOG_LEVEL=DEBUG
```
Максимум информации для отладки

### Staging
```env
LOG_LEVEL=INFO
```
Баланс между информативностью и производительностью

### Production
```env
LOG_LEVEL=WARNING
```
Только важная информация, минимум overhead

## 📦 Размер логов

Ожидаемый объём:
- 🟢 Низкая нагрузка: ~1-5 MB/день
- 🟡 Средняя нагрузка: ~10-50 MB/день
- 🔴 Высокая нагрузка: ~100-500 MB/день

Логи автоматически удаляются через `LOG_RETENTION_DAYS` дней.

## 🚀 Запуск приложения

```bash
# Запуск с логированием
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Просмотр логов в реальном времени
tail -f logs/elia-app-$(date +%Y-%m-%d).log
```

## 🆘 Troubleshooting

### Логи не создаются
```bash
# Проверьте права
ls -la logs/

# Создайте директорию вручную
mkdir -p logs
```

### Слишком много логов
```env
# Увеличьте уровень
LOG_LEVEL=WARNING

# Уменьшите срок хранения
LOG_RETENTION_DAYS=7
```

### Медленная работа
```env
# Используйте INFO в продакшене
LOG_LEVEL=INFO

# Проверьте место на диске
df -h
```

## 🔐 Безопасность

Чувствительные данные автоматически скрываются:
- ❌ Пароли
- ❌ Токены
- ❌ API ключи
- ❌ Authorization headers
- ❌ Cookies

## 🎓 Лучшие практики

### ✅ DO
```python
logger.info(f"Создан пациент: id={id}, name={name}")
logger.exception(f"Ошибка: {str(e)}")
if duration > 1.0:
    logger.warning(f"Медленная операция: {duration}s")
```

### ❌ DON'T
```python
logger.info(f"Password: {password}")  # НЕ логировать чувствительные данные
print("Debug info")                    # Использовать logger, не print
for item in items:
    logger.info(item)                  # НЕ логировать в циклах
```

## 📈 Будущие улучшения

- [ ] ELK Stack интеграция
- [ ] Grafana Loki для визуализации
- [ ] Sentry для мониторинга ошибок
- [ ] Структурированное логирование (JSON)
- [ ] Метрики производительности
- [ ] CloudWatch / Azure Monitor

---

**Версия**: 1.0.0  
**Дата**: 26.10.2025  
**Статус**: ✅ Полностью протестировано и работает

