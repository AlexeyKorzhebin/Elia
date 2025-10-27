# Шпаргалки и быстрые справочники

Коллекция полезных шпаргалок и быстрых справочников для работы с Elia Platform.

---

## 📋 Доступные шпаргалки

### 🐳 Docker
**Файл**: [`docker-cheatsheet.txt`](docker-cheatsheet.txt)

Быстрая справка по командам Docker для работы с Elia Platform:
- Сборка образов
- Управление контейнерами
- Просмотр логов
- Отладка проблем

```bash
cat docs/cheatsheets/docker-cheatsheet.txt
```

---

### 🚀 Развёртывание
**Файл**: [`deploy-parameters-cheatsheet.txt`](deploy-parameters-cheatsheet.txt)

Параметры и переменные окружения для развёртывания:
- Переменные .env
- Настройки сервера
- Конфигурация OpenAI

```bash
cat docs/cheatsheets/deploy-parameters-cheatsheet.txt
```

---

### 📜 Скрипты развёртывания
**Файл**: [`deploy-script-cheatsheet.txt`](deploy-script-cheatsheet.txt)

Команды и примеры использования скриптов развёртывания:
- build-and-push.sh
- deploy-ubuntu.sh
- Управление сервером

```bash
cat docs/cheatsheets/deploy-script-cheatsheet.txt
```

---

### 🔐 SSH доступ
**Файл**: [`ssh-quick-reference.txt`](ssh-quick-reference.txt)

Быстрая справка по SSH командам и скриптам:
- Подключение к серверу
- Управление приложением
- Копирование файлов
- Docker команды

```bash
cat docs/cheatsheets/ssh-quick-reference.txt
```

---

### ⚙️ Systemd управление
**Файл**: [`systemd-cheatsheet.txt`](systemd-cheatsheet.txt)

Команды для управления сервисом через systemd:
- Запуск/остановка/перезапуск
- Автозапуск при загрузке
- Просмотр логов
- Диагностика проблем

```bash
cat docs/cheatsheets/systemd-cheatsheet.txt
```

---

### 📊 Мониторинг ресурсов
**Файл**: [`monitoring-cheatsheet.txt`](monitoring-cheatsheet.txt)

Команды для мониторинга использования ресурсов:
- CPU и память контейнера
- Использование диска
- Сетевая активность
- Системные показатели
- Диагностика проблем

```bash
cat docs/cheatsheets/monitoring-cheatsheet.txt
# Или используйте скрипт
./scripts/server-resources.sh
```

---

## 🎯 Как использовать

### Просмотр шпаргалки

```bash
# В терминале
cat docs/cheatsheets/имя-файла.txt

# Или откройте в редакторе
vim docs/cheatsheets/имя-файла.txt
```

### Поиск в шпаргалках

```bash
# Найти команду во всех шпаргалках
grep -r "docker ps" docs/cheatsheets/

# Найти в конкретной шпаргалке
grep "ssh" docs/cheatsheets/ssh-quick-reference.txt
```

### Печать шпаргалки

```bash
# Распечатать для удобного доступа
cat docs/cheatsheets/docker-cheatsheet.txt | lpr
```

---

## 📝 Добавление новой шпаргалки

1. Создайте txt файл в этой папке
2. Используйте понятную структуру с заголовками
3. Добавьте примеры команд
4. Обновите этот README.md

### Шаблон шпаргалки

```
═══════════════════════════════════════════════════════════════════
  НАЗВАНИЕ ШПАРГАЛКИ
═══════════════════════════════════════════════════════════════════

РАЗДЕЛ 1
───────────────────────────────────────────────────────────────────

Описание команды:
   команда --параметры

Пример:
   команда --пример
```

---

## 🔗 См. также

- [Документация проекта](../)
- [Скрипты управления](../../scripts/README.md)
- [Главный README](../../README.md)

---

**Совет**: Держите эти шпаргалки под рукой для быстрого доступа к часто используемым командам!

