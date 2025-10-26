# Руководство по логированию

## Обзор системы логирования

Проект использует продвинутую систему логирования на основе стандартной библиотеки Python `logging` с автоматической ротацией логов по дням.

## Структура логов

### Директория логов
```
logs/
├── elia-app-2025-10-26.log       # Все логи приложения
├── elia-errors-2025-10-26.log    # Только ошибки (ERROR и выше)
└── elia-access-2025-10-26.log    # HTTP access логи
```

### Автоматическая ротация
- **Ротация**: Каждый день в полночь создаётся новый файл с текущей датой
- **Хранение**: Логи хранятся по умолчанию 30 дней (настраивается в `config.py`)
- **Автоочистка**: Старые логи удаляются автоматически

## Настройка логирования

### Конфигурация (config.py)

```python
class Settings(BaseSettings):
    # Logging
    log_level: str = "INFO"          # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_dir: str = "logs"            # Директория для логов
    log_retention_days: int = 30     # Дней хранения логов
```

### Переменные окружения (.env)

```env
# Уровни логирования
LOG_LEVEL=INFO              # Для продакшена
# LOG_LEVEL=DEBUG           # Для разработки

# Директория логов
LOG_DIR=logs

# Срок хранения логов (дней)
LOG_RETENTION_DAYS=30
```

## Использование логирования в коде

### Базовое использование

```python
from app.logger import get_logger

logger = get_logger(__name__)

# Различные уровни логирования
logger.debug("Детальная отладочная информация")
logger.info("Общая информация о работе")
logger.warning("Предупреждение о потенциальной проблеме")
logger.error("Ошибка, требующая внимания")
logger.critical("Критическая ошибка")
```

### Логирование с контекстом

```python
# Хорошо: логируем с контекстом
logger.info(f"Создан пациент: patient_id={patient.id}, name={patient.full_name}")

# Плохо: без контекста
logger.info("Создан пациент")
```

### Логирование исключений

```python
try:
    result = await some_operation()
except Exception as e:
    # Автоматически логирует stack trace
    logger.exception(f"Ошибка при выполнении операции: {str(e)}")
    raise
```

## Уровни логирования

### DEBUG
**Когда использовать**: Детальная информация для отладки
```python
logger.debug(f"Параметры запроса: search={search}, limit={limit}")
logger.debug(f"Промежуточный результат расчета: {intermediate_value}")
```

### INFO
**Когда использовать**: Общая информация о нормальной работе
```python
logger.info(f"Пользователь вошел в систему: user_id={user_id}")
logger.info(f"Обработано {count} записей за {duration}ms")
```

### WARNING
**Когда использовать**: Предупреждения о необычных ситуациях
```python
logger.warning(f"Медленный запрос: {duration}ms > 1000ms")
logger.warning(f"Пациент не найден: patient_id={patient_id}")
```

### ERROR
**Когда использовать**: Ошибки, требующие внимания
```python
logger.error(f"Не удалось подключиться к БД: {str(e)}")
logger.error(f"Не удалось отправить в МИС: appointment_id={id}")
```

### CRITICAL
**Когда использовать**: Критические ошибки
```python
logger.critical("База данных недоступна!")
logger.critical("Закончилось место на диске")
```

## Лучшие практики

### ✅ DO (Делать)

1. **Используйте правильный уровень логирования**
   ```python
   logger.debug("Отладочная информация")
   logger.info("Важная информация")
   logger.error("Ошибка")
   ```

2. **Логируйте с контекстом**
   ```python
   logger.info(f"Создан отчёт: appointment_id={id}, patient={name}")
   ```

3. **Используйте logger.exception() для исключений**
   ```python
   try:
       await operation()
   except Exception as e:
       logger.exception(f"Ошибка операции: {str(e)}")
       raise
   ```

4. **Логируйте начало и завершение важных операций**
   ```python
   logger.info(f"Начало экспорта данных: {params}")
   # ... операция ...
   logger.info(f"Экспорт завершён: обработано {count} записей")
   ```

5. **Логируйте медленные операции**
   ```python
   if duration > 1.0:
       logger.warning(f"Медленная операция: {duration}s")
   ```

### ❌ DON'T (Не делать)

1. **Не логируйте чувствительные данные**
   ```python
   # ❌ Плохо
   logger.info(f"Пользователь: password={password}")
   
   # ✅ Хорошо
   logger.info(f"Пользователь авторизован: user_id={user_id}")
   ```

2. **Не используйте print() вместо logging**
   ```python
   # ❌ Плохо
   print(f"Ошибка: {error}")
   
   # ✅ Хорошо
   logger.error(f"Ошибка: {error}")
   ```

3. **Не логируйте в циклах без ограничения**
   ```python
   # ❌ Плохо
   for item in items:  # 10000 записей
       logger.info(f"Обработан: {item}")
   
   # ✅ Хорошо
   logger.info(f"Начало обработки {len(items)} записей")
   for i, item in enumerate(items):
       if i % 100 == 0:
           logger.debug(f"Обработано {i}/{len(items)}")
   logger.info(f"Обработка завершена")
   ```

4. **Не дублируйте логи**
   ```python
   # ❌ Плохо
   logger.error(f"Ошибка: {e}")
   logger.exception(e)  # Дублирует информацию
   
   # ✅ Хорошо
   logger.exception(f"Ошибка при операции: {str(e)}")
   ```

5. **Не используйте конкатенацию строк**
   ```python
   # ❌ Плохо
   logger.info("User " + str(user_id) + " logged in")
   
   # ✅ Хорошо
   logger.info(f"User {user_id} logged in")
   ```

## Примеры использования

### API endpoints

```python
from app.logger import get_logger

logger = get_logger(__name__)

@router.get("/{id}")
async def get_item(id: int, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Запрос элемента: id={id}")
    
    try:
        item = await crud.get_item(db, id)
        if not item:
            logger.warning(f"Элемент не найден: id={id}")
            raise HTTPException(status_code=404, detail="Not found")
        
        logger.info(f"Получен элемент: id={id}, name={item.name}")
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении элемента {id}: {str(e)}")
        raise
```

### Бизнес-логика

```python
from app.logger import get_logger

logger = get_logger(__name__)

async def process_medical_report(appointment_id: int):
    logger.info(f"Начало обработки отчёта: appointment_id={appointment_id}")
    
    try:
        # Валидация
        if not await validate_data(appointment_id):
            logger.warning(f"Валидация не пройдена: appointment_id={appointment_id}")
            return False
        
        # Обработка
        result = await process_data(appointment_id)
        
        logger.info(
            f"Отчёт успешно обработан: appointment_id={appointment_id}, "
            f"records={result.records_count}, duration={result.duration}ms"
        )
        return True
        
    except Exception as e:
        logger.exception(
            f"Ошибка при обработке отчёта: appointment_id={appointment_id}"
        )
        raise
```

## HTTP Access логи

Access логи автоматически создаются middleware и включают:
- IP адрес клиента
- HTTP метод и путь
- Статус код ответа
- Время обработки запроса

Пример:
```
2025-10-26 14:30:45 - 127.0.0.1 - "GET /api/patients/123" 200 - 45.23ms
2025-10-26 14:30:50 - 127.0.0.1 - "POST /api/appointments" 201 - 120.45ms
```

## Мониторинг логов

### Просмотр логов в реальном времени

```bash
# Все логи
tail -f logs/elia-app-$(date +%Y-%m-%d).log

# Только ошибки
tail -f logs/elia-errors-$(date +%Y-%m-%d).log

# Access логи
tail -f logs/elia-access-$(date +%Y-%m-%d).log
```

### Поиск в логах

```bash
# Найти все ERROR за сегодня
grep "ERROR" logs/elia-app-$(date +%Y-%m-%d).log

# Найти логи для конкретного пациента
grep "patient_id=123" logs/elia-app-*.log

# Найти медленные запросы
grep "Медленный запрос" logs/elia-app-*.log
```

### Анализ логов

```bash
# Подсчёт ошибок по типам
grep "ERROR" logs/elia-app-*.log | cut -d'-' -f4 | sort | uniq -c

# Топ медленных запросов
grep "ms" logs/elia-access-*.log | sort -t'-' -k5 -n | tail -20
```

## Производительность

### Рекомендации

1. **DEBUG уровень только для разработки**
   - В продакшене используйте INFO или WARNING
   - DEBUG создаёт много логов и замедляет приложение

2. **Асинхронное логирование**
   - Текущая реализация не блокирует основной поток
   - Логи буферизуются для лучшей производительности

3. **Размер логов**
   - Средний размер логов: ~1-5 MB в день для небольшого приложения
   - При активном использовании: ~50-100 MB в день
   - Настройте `log_retention_days` соответственно

## Интеграция с мониторингом

### Будущие улучшения

1. **ELK Stack** (Elasticsearch, Logstash, Kibana)
2. **Grafana Loki** для визуализации
3. **Sentry** для отслеживания ошибок
4. **CloudWatch** / **Azure Monitor** для облачных сред

## Troubleshooting

### Логи не создаются

1. Проверьте права доступа к директории `logs/`
2. Проверьте настройки в `.env`
3. Проверьте уровень логирования

### Слишком много логов

1. Увеличьте уровень логирования (DEBUG → INFO → WARNING)
2. Уменьшите `log_retention_days`
3. Добавьте фильтры для ненужных логов

### Медленная работа

1. Проверьте размер файлов логов
2. Переключите DEBUG на INFO в продакшене
3. Проверьте место на диске

## Контрольный чеклист

- [ ] Используете правильный уровень логирования
- [ ] Логируете с контекстом (ID, имена, параметры)
- [ ] Не логируете чувствительные данные
- [ ] Используете logger.exception() для исключений
- [ ] Настроили правильный LOG_LEVEL для окружения
- [ ] Настроили адекватный log_retention_days
- [ ] Мониторите размер логов
- [ ] Регулярно проверяете логи ошибок

