# Elia Design System

Дизайн-система проекта Elia, основанная на дизайне из Figma.

## Цветовая палитра

Основная цветовая палитра, извлеченная из Figma:

### Основные цвета

```css
--elia-dark: #1A1A1A        /* Темный текст, основной контраст */
--elia-lavender: #D0BAFF    /* Лавандовый - основной цвет бренда */
--elia-white: #FFFFFF       /* Белый фон */
```

### Акцентные цвета для секций

```css
--elia-cyan: #CFFAFE        /* Бирюзовый - для блока "Основные данные" */
--elia-pink: #FCE7F3        /* Розовый - для блока "Хронические заболевания" */
--elia-yellow: #FEF3C7      /* Желтый - для блока "Последние заболевания" */
--elia-green: #D1FAE5       /* Зеленый - для блока "Основные показатели здоровья" */
```

### Нейтральные цвета

```css
--elia-gray-50: #F9FAFB
--elia-gray-100: #F3F4F6
--elia-gray-200: #E5E7EB
--elia-gray-600: #6B7280
```

## Логотип

### Файлы логотипа

- `/static/images/logo.svg` - Полный логотип с текстом (120x40px)

### Использование в HTML

```html
<!-- Логотип -->
<img src="/static/images/logo.svg" alt="Elia" width="120" height="40">
```

### Характеристики логотипа

- Формат: SVG с градиентом
- Символ: Стилизованная медицинская иконка с текстом "elia"
- Градиент: От лавандового (#D0BAFF) до бирюзового (#A5EAED)
- Размеры: 139x44 (масштабируется до 120x40)

## Типографика

### Заголовки

- **H1**: `text-3xl font-semibold` (30px)
- **H2**: `text-2xl font-semibold` (24px)
- **H3**: `text-xl font-semibold` (20px)

### Основной текст

- **Body**: `text-base` (16px)
- **Small**: `text-sm` (14px)
- **Extra small**: `text-xs` (12px)

### Font weights

- Normal: 400
- Medium: 500
- Semibold: 600
- Bold: 700

## Компоненты

### Кнопки

#### Основная кнопка (Primary)

```html
<button class="px-5 py-2.5 text-sm text-elia-dark bg-elia-lavender rounded-xl hover:bg-opacity-90 font-medium transition-all hover:shadow-lg">
    Текст кнопки
</button>
```

#### Вторичная кнопка (Secondary)

```html
<button class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
    Текст кнопки
</button>
```

#### Outline кнопка

```html
<button class="px-4 py-2 text-sm text-elia-dark border border-elia-lavender rounded-lg hover:bg-elia-lavender hover:bg-opacity-20">
    Текст кнопки
</button>
```

### Карточки

#### Карточка приема пациента

```html
<div class="appointment-card flex-shrink-0 w-64 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
    <!-- Содержимое -->
</div>
```

#### Активная карточка

```html
<div class="appointment-card active bg-elia-lavender text-elia-dark">
    <!-- Содержимое -->
</div>
```

### Бейджи (Badges)

```html
<!-- Бирюзовый -->
<span class="badge badge-cyan">Анализ</span>

<!-- Розовый -->
<span class="badge badge-pink">Головная боль</span>

<!-- Желтый -->
<span class="badge badge-yellow">Направление на анализы</span>

<!-- Лавандовый -->
<span class="badge badge-purple">Запланирован</span>
```

### Секции с цветовой кодировкой

```html
<!-- Бирюзовая секция (Основные данные) -->
<div class="section-cyan">
    <h3 class="section-header">Основные данные</h3>
    <!-- Содержимое -->
</div>

<!-- Розовая секция (Хронические заболевания) -->
<div class="section-pink">
    <h3 class="section-header">Хронические заболевания</h3>
    <!-- Содержимое -->
</div>

<!-- Желтая секция (Последние заболевания) -->
<div class="section-yellow">
    <h3 class="section-header">Последние заболевания</h3>
    <!-- Содержимое -->
</div>

<!-- Зеленая секция (Показатели здоровья) -->
<div class="section-green">
    <h3 class="section-header">Основные показатели здоровья</h3>
    <!-- Содержимое -->
</div>
```

### Input поля

```html
<input 
    type="text" 
    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-elia-lavender"
    placeholder="Введите текст">
```

### Меню навигации

#### Активный пункт меню

```html
<a href="/" class="flex items-center space-x-3 px-4 py-3 rounded-xl text-elia-dark bg-elia-lavender font-medium">
    <svg><!-- иконка --></svg>
    <span>Мои пациенты</span>
</a>
```

#### Неактивный пункт меню

```html
<a href="/organization" class="flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-600 hover:bg-gray-50 transition-colors">
    <svg><!-- иконка --></svg>
    <span>Организация</span>
</a>
```

## Скругления (Border Radius)

- Маленькие элементы (badges): `12px` или `rounded-xl`
- Кнопки и inputs: `8px` или `12px` (`rounded-lg` или `rounded-xl`)
- Карточки: `12px` или `16px` (`rounded-lg` или `rounded-2xl`)

## Тени (Shadows)

```css
/* Легкая тень (карточки) */
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

/* Средняя тень (при hover) */
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

/* Тень для лавандовых элементов */
box-shadow: 0 4px 12px rgba(208, 186, 255, 0.3);
```

## Tailwind конфигурация

В `tailwind.config` добавлены следующие пользовательские цвета:

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                'elia-dark': '#1A1A1A',
                'elia-lavender': '#D0BAFF',
                'elia-cyan': '#CFFAFE',
                'elia-pink': '#FCE7F3',
                'elia-yellow': '#FEF3C7',
                'elia-green': '#D1FAE5',
            }
        }
    }
}
```

## Использование в JavaScript

### Обновление классов при смене состояния

```javascript
// Активация вкладки
$('.tab-button').removeClass('tab-active bg-elia-lavender text-elia-dark')
    .addClass('bg-gray-100 text-gray-700');
$(targetButton).removeClass('bg-gray-100 text-gray-700')
    .addClass('tab-active');
```

### Лоадер

```javascript
Utils.showLoader('Загрузка...')
// Возвращает HTML с лавандовым spinner
```

## Принципы использования цветов

1. **Лавандовый (#D0BAFF)** - основной цвет бренда:
   - Активные состояния
   - Главные кнопки
   - Выделенные элементы
   - Логотип

2. **Темный (#1A1A1A)** - для текста:
   - Основной текст
   - Заголовки
   - Текст на лавандовом фоне

3. **Акцентные цвета** - для категоризации:
   - Бирюзовый - основная информация
   - Розовый - проблемы/заболевания
   - Желтый - предупреждения/направления
   - Зеленый - здоровье/показатели

4. **Белый** - для фонов и контраста

## Миграция со старых цветов

Старые цвета заменены следующим образом:

| Старый цвет | Новый цвет | Использование |
|------------|-----------|---------------|
| `elia-purple` (#8B5CF6) | `elia-lavender` (#D0BAFF) | Основной цвет бренда |
| `elia-blue` (#60A5FA) | Убран | Больше не используется в градиентах |
| `bg-purple-50` | `bg-elia-lavender` | Активные состояния |
| `text-purple` | `text-elia-dark` | Текст на светлых фонах |

## Анимации и переходы

```css
/* Базовый переход для всех элементов */
transition: all 0.2s ease-in-out;

/* Для кнопок */
transition: all 0.2s;
transition-all hover:shadow-lg

/* Для карточек */
transition: transform 0.2s, box-shadow 0.2s;
```

## Адаптивность

Дизайн оптимизирован для:
- Desktop: 1920px+
- Laptop: 1366px+
- Tablet: 768px+ (боковая панель остается видимой)
- Mobile: < 768px (боковая панель скрывается)

---

*Последнее обновление: 26 октября 2025*
*На основе дизайна из Figma*

