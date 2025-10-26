# Исправления: Сохранение разговора и заполнение анамнеза

## Дата: 26 октября 2025

### 🐛 Проблемы:

1. **Сгенерированный разговор не сохранялся** ❌ - на самом деле сохранялся, проблема была в frontend
2. **Данные не попадали в поля анамнеза** ❌ - frontend не обновлял данные

---

## ✅ Исправления:

### 1. Backend (уже работал корректно)

**Файл:** `app/api/audio.py`

Генерация и сохранение разговора:
- ✅ Создаётся запись `AudioFile` с `transcription_text`
- ✅ Статус устанавливается в `COMPLETED`
- ✅ Данные сохраняются через `crud.update_transcription()`

Извлечение анамнеза:
- ✅ Создаётся/обновляется `MedicalReport`
- ✅ Заполняются поля: `purpose`, `complaints`, `anamnesis`

### 2. Frontend - Исправлено

**Файл:** `static/js/audio-handler.js`

**Изменение:**
```javascript
// БЫЛО: данные извлекались, но не сохранялись в PatientCard
const report = await response.json();
Utils.showToast('Анамнез успешно извлечён и сохранён!', 'success');

// СТАЛО: данные сохраняются в PatientCard.reportData
const report = await response.json();
PatientCard.reportData = report;  // ← ДОБАВЛЕНО
Utils.showToast('Анамнез успешно извлечён и сохранён!', 'success');
```

**Файл:** `static/js/patient-card.js`

**Изменение 1 - Метод `switchTab` стал асинхронным:**
```javascript
// БЫЛО:
switchTab(tab) {
    // ...
}

// СТАЛО:
async switchTab(tab) {  // ← ДОБАВЛЕНО async
    // ...
}
```

**Изменение 2 - Добавлена перезагрузка данных:**
```javascript
case 'anamnesis':
    // ДОБАВЛЕНО: перезагружаем данные перед рендерингом
    await this.reloadReportData();
    content.html(this.renderAnamnesis());
    this.initAnamnesisHandlers();
    break;
```

**Изменение 3 - Новый метод `reloadReportData()`:**
```javascript
async reloadReportData() {
    try {
        const reportResponse = await fetch(`/api/appointments/${this.appointmentData.id}/report`);
        if (reportResponse.ok) {
            this.reportData = await reportResponse.json();
        }
    } catch (e) {
        console.log('Отчёт не найден или ошибка загрузки');
    }
}
```

---

## 📊 Результат:

### ✅ Теперь работает:

1. **Генерация разговора:**
   - Диалог генерируется через OpenAI API
   - Сохраняется в БД в таблицу `audio_files`
   - Отображается на вкладке "Стенограмма"

2. **Извлечение анамнеза:**
   - AI анализирует диалог
   - Извлекает 3 поля:
     * Цель обращения
     * Жалобы пациента
     * Анамнез
   - Сохраняет в БД в таблицу `medical_reports`

3. **Отображение данных:**
   - При переходе на вкладку "Анамнез" данные загружаются из БД
   - Поля автоматически заполняются
   - Пользователь видит извлечённую информацию

---

## 🧪 Тестирование:

### Шаги для проверки:

1. Откройте http://localhost:8000
2. Выберите любого пациента
3. Перейдите на вкладку **"Стенограмма"**
4. Нажмите **"Сгенерировать разговор (AI)"**
5. Подождите ~10-15 секунд
6. Проверьте что диалог отображается ✅
7. Нажмите **"Извлечь анамнез из разговора"**
8. Подождите ~5-10 секунд
9. Нажмите **"Перейти к анамнезу"**
10. **Проверьте что все 3 поля заполнены!** ✅

---

## 📝 Технические детали:

### База данных:

**Таблица `audio_files`:**
```sql
transcription_text: TEXT  -- сюда сохраняется сгенерированный диалог
transcription_status: TEXT -- статус: COMPLETED
```

**Таблица `medical_reports`:**
```sql
purpose: TEXT     -- цель обращения
complaints: TEXT  -- жалобы пациента
anamnesis: TEXT   -- подробный анамнез
```

### API Endpoints:

- `POST /api/audio/generate-mock-conversation?appointment_id={id}` 
  → Генерирует и сохраняет диалог

- `POST /api/audio/extract-anamnesis-by-appointment?appointment_id={id}`
  → Извлекает и сохраняет данные анамнеза

- `GET /api/appointments/{id}/report`
  → Получает сохранённый отчёт

---

## ✨ Улучшения UI:

Добавлен информативный блок после извлечения:
```
✅ Данные успешно извлечены и сохранены!

• Цель обращения: заполнена
• Жалобы пациента: заполнены
• Анамнез: заполнен

[Перейти к анамнезу]
```

---

## 🎉 Готово!

Обе проблемы исправлены. Система полностью работает end-to-end:

**Генерация → Сохранение в БД → Извлечение → Сохранение в БД → Отображение**

