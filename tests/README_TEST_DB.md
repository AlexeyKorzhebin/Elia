# Настройка тестовой базы данных

## Обзор

Все pytest тесты используют **отдельную тестовую базу данных** `elia-test.db`, которая **не затрагивает продуктовую БД** `elia.db`.

## Автоматическая настройка

При первом запуске тестов:
1. Создаётся файл `elia-test.db` (если его нет)
2. Создаются все необходимые таблицы
3. Тесты используют эту БД для всех операций

## Переменные окружения

### `TEST_DATABASE_PATH`
Путь к тестовой БД (по умолчанию: `elia-test.db`)

```bash
export TEST_DATABASE_PATH="custom-test.db"
pytest tests/ -v
```

### `CLEAN_TEST_DB`
Очистить БД перед запуском тестов (удалить файл если существует)

```bash
export CLEAN_TEST_DB=1
pytest tests/ -v
```

### `CLEAN_TEST_DB_AFTER`
Очистить БД после завершения всех тестов

```bash
export CLEAN_TEST_DB_AFTER=1
pytest tests/ -v
```

## Примеры использования

### Базовый запуск
```bash
# БД создастся автоматически
pytest tests/test_quick_check.py -v
```

### Очистка перед тестами
```bash
# Удалить старую БД и создать новую
export CLEAN_TEST_DB=1
pytest tests/ -v
```

### Очистка после тестов
```bash
# Удалить БД после завершения всех тестов
export CLEAN_TEST_DB_AFTER=1
pytest tests/ -v
```

### Кастомный путь к БД
```bash
# Использовать другую БД для тестов
export TEST_DATABASE_PATH="tests/fixtures/test.db"
pytest tests/ -v
```

## Проверка тестовой БД

После запуска тестов можно проверить содержимое:

```bash
# Список таблиц
sqlite3 elia-test.db ".tables"

# Пациенты
sqlite3 elia-test.db "SELECT id, first_name, last_name FROM patients;"

# Приёмы
sqlite3 elia-test.db "SELECT id, appointment_date, status FROM appointments;"

# Аудиофайлы
sqlite3 elia-test.db "SELECT id, filename, transcription_status FROM audio_files;"

# Медицинские отчёты
sqlite3 elia-test.db "SELECT id, purpose, submitted_to_mis FROM medical_reports;"
```

## E2E тесты

⚠️ **Важно**: E2E тесты (`test_e2e.py`) запускают реальный сервер и могут использовать продуктовую БД, если не настроена переменная окружения.

Для использования тестовой БД в E2E тестах:

```bash
# Установите переменную окружения перед запуском E2E тестов
export DATABASE_URL="sqlite+aiosqlite:///./elia-test.db"
pytest tests/test_e2e.py -v
```

Или создайте `.env.test` файл:
```env
DATABASE_URL=sqlite+aiosqlite:///./elia-test.db
```

## Безопасность

✅ **Продуктовая БД защищена**:
- Все pytest тесты используют только `elia-test.db`
- Продуктовая БД `elia.db` не затрагивается
- Тестовая БД добавлена в `.gitignore`

⚠️ **Рекомендации**:
- Не коммитьте `elia-test.db` в Git (уже в `.gitignore`)
- Используйте `CLEAN_TEST_DB=1` для чистых тестов
- Проверяйте путь к БД перед запуском тестов

## Структура файлов

```
.
├── elia.db              # Продуктовая БД (не трогается тестами)
├── elia-test.db         # Тестовая БД (создаётся автоматически)
├── tests/
│   ├── conftest.py      # Конфигурация тестовой БД
│   └── ...
└── .gitignore           # Содержит *.db (игнорирует обе БД)
```

## Устранение проблем

### БД не создаётся
```bash
# Проверьте права на запись в директорию
ls -la elia-test.db
chmod 644 elia-test.db  # если нужно
```

### Ошибка "database is locked"
```bash
# Закройте все соединения с БД
# Удалите БД и запустите тесты заново
rm elia-test.db
pytest tests/ -v
```

### Хотите использовать in-memory БД
Измените в `tests/conftest.py`:
```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

Но тогда данные не сохранятся между запусками тестов.

