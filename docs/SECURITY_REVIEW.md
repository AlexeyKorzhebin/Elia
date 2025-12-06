# Ревью безопасности кода

Дата: 2025-12-03  
Версия: 1.0.0

## 🔴 Критические проблемы

### 1. Отсутствие аутентификации и авторизации

**Проблема:** Все API endpoints доступны без проверки прав доступа. Любой пользователь может:
- Просматривать данные всех пациентов
- Изменять медицинские отчеты
- Загружать и удалять аудиофайлы
- Извлекать персональные данные

**Расположение:**
- `app/main.py` - все endpoints
- `app/api/patients.py` - endpoints пациентов
- `app/api/appointments.py` - endpoints приёмов
- `app/api/audio.py` - endpoints аудио

**Рекомендации:**
```python
# Добавить dependency для проверки аутентификации
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Проверка токена
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен доступа"
        )
    return token

# Использовать в endpoints
@router.get("/{patient_id}")
async def get_patient_detail(
    patient_id: int,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    # Проверка прав доступа к конкретному пациенту
    if not has_access_to_patient(token, patient_id):
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    # ...
```

### 2. Небезопасная конфигурация CORS

**Проблема:** CORS настроен на разрешение всех источников (`allow_origins=["*"]`), что позволяет любому сайту делать запросы к API.

**Расположение:** `app/main.py:67-73`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ ОПАСНО!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Рекомендации:**
```python
# Для production использовать конкретные домены
allowed_origins = settings.allowed_origins.split(",") if hasattr(settings, 'allowed_origins') else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Process-Time"],
)
```

### 3. Потенциальная SQL Injection через ILIKE

**Проблема:** Использование f-строк в SQL-запросах с ILIKE может быть уязвимо, хотя SQLAlchemy обычно защищает от этого.

**Расположение:** `app/crud.py:40-45`

```python
if search:
    search_filter = or_(
        Patient.first_name.ilike(f"%{search}%"),  # ⚠️ Потенциально небезопасно
        Patient.last_name.ilike(f"%{search}%"),
        Patient.middle_name.ilike(f"%{search}%")
    )
```

**Рекомендации:**
```python
# SQLAlchemy автоматически экранирует, но лучше явно валидировать
from pydantic import validate_call

@validate_call
async def get_patients(
    db: AsyncSession, 
    search: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 100
) -> Sequence[Patient]:
    # Валидация и санитизация поискового запроса
    if search:
        # Удаляем опасные символы
        search = search.strip()[:100]  # Ограничение длины
        if not search.replace(" ", "").replace("-", "").isalnum():
            raise ValueError("Недопустимые символы в поисковом запросе")
        
        search_filter = or_(
            Patient.first_name.ilike(f"%{search}%"),
            Patient.last_name.ilike(f"%{search}%"),
            Patient.middle_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
```

### 4. Недостаточная валидация загружаемых файлов

**Проблема:** Проверяется только расширение и MIME-тип, но не содержимое файла. Возможна загрузка вредоносных файлов.

**Расположение:** `app/api/audio.py:58-64`, `app/api/patients.py:112-118`

**Рекомендации:**
```python
import magic  # python-magic
import hashlib

async def validate_file_content(file_content: bytes, expected_type: str) -> bool:
    """Проверка реального содержимого файла"""
    # Проверка magic bytes
    file_type = magic.from_buffer(file_content, mime=True)
    
    if expected_type == "audio":
        allowed_audio_types = ["audio/mpeg", "audio/wav", "audio/x-wav"]
        return file_type in allowed_audio_types
    elif expected_type == "image":
        allowed_image_types = ["image/jpeg", "image/png", "image/heic"]
        return file_type in allowed_image_types
    
    return False

# Проверка размера файла перед чтением
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

async def upload_audio_file(...):
    # Проверка размера заголовка Content-Length
    if request.headers.get("content-length"):
        if int(request.headers["content-length"]) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Файл слишком большой")
    
    # Читаем первые байты для проверки
    file_content = await file.read(1024)
    await file.seek(0)  # Возвращаемся к началу
    
    if not await validate_file_content(file_content, "audio"):
        raise HTTPException(status_code=400, detail="Неверный формат файла")
```

### 5. Path Traversal при загрузке файлов

**Проблема:** Использование `file.filename` без санитизации может привести к path traversal атакам.

**Расположение:** `app/api/audio.py:59, 95`

**Рекомендации:**
```python
from pathlib import Path
import re

def sanitize_filename(filename: str) -> str:
    """Очистка имени файла от опасных символов"""
    # Удаляем путь, оставляем только имя
    filename = Path(filename).name
    # Удаляем опасные символы
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    # Ограничиваем длину
    return filename[:255]

# Использование
safe_filename = sanitize_filename(file.filename)
unique_filename = f"{uuid.uuid4()}{Path(safe_filename).suffix.lower()}"
```

## 🟡 Серьёзные проблемы

### 6. Отсутствие Rate Limiting

**Проблема:** Нет ограничения частоты запросов, что позволяет DoS атаки и злоупотребление API.

**Рекомендации:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/upload")
@limiter.limit("10/minute")  # 10 запросов в минуту
async def upload_audio_file(...):
    # ...
```

### 7. Отсутствие CSRF защиты

**Проблема:** Нет защиты от CSRF атак для state-changing операций (POST, PUT, DELETE).

**Рекомендации:**
```python
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings(secret_key=settings.secret_key)

@router.post("/{appointment_id}/report")
async def create_update_medical_report(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
    # ...
):
    await csrf_protect.validate_csrf(request)
    # ...
```

### 8. Логирование чувствительных данных

**Проблема:** В логи могут попадать персональные данные пациентов и медицинская информация.

**Расположение:** `app/middleware.py`, различные endpoints

**Рекомендации:**
```python
import re

def sanitize_log_data(data: str) -> str:
    """Удаление ПДн из логов"""
    # Маскирование ФИО
    data = re.sub(r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\b', 
                  '[ФИО скрыто]', data)
    # Маскирование дат рождения
    data = re.sub(r'\d{2}\.\d{2}\.\d{4}', '[дата скрыта]', data)
    return data

logger.info(f"Получены детали пациента: {sanitize_log_data(patient.full_name)}")
```

### 9. Отсутствие Security Headers

**Проблема:** Не установлены важные security headers (HSTS, CSP, X-Frame-Options и т.д.).

**Рекомендации:**
```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

### 10. Небезопасное хранение секретов

**Проблема:** API ключи хранятся в `.env`, но нет проверки что файл не коммитится в git.

**Расположение:** `app/config.py:36`

**Рекомендации:**
```python
# Добавить проверку в CI/CD
# .github/workflows/security.yml
- name: Check for secrets
  run: |
    if grep -r "OPENAI_API_KEY" . --exclude-dir=.git; then
      echo "ERROR: Secrets found in code!"
      exit 1
    fi

# Использовать переменные окружения напрямую без .env файла
# Или использовать секретные менеджеры (AWS Secrets Manager, HashiCorp Vault)
```

### 11. Отсутствие валидации размера запросов

**Проблема:** Нет ограничения размера тела запроса, что может привести к DoS.

**Рекомендации:**
```python
from fastapi import Request
from fastapi.exceptions import RequestValidationError

MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            raise HTTPException(status_code=413, detail="Request too large")
    return await call_next(request)
```

## 🟢 Рекомендации по улучшению

### 12. Валидация входных данных

**Текущее состояние:** Используется Pydantic, но не везде.

**Рекомендации:**
- Добавить валидацию для всех входных параметров
- Использовать `Field` с ограничениями
- Добавить кастомные валидаторы

```python
from pydantic import BaseModel, Field, field_validator

class BloodPressureUpdateRequest(BaseModel):
    systolic: int = Field(..., ge=60, le=300)
    diastolic: int = Field(..., ge=30, le=200)
    pulse: Optional[int] = Field(None, ge=30, le=250)
    source: str = Field(default="manual", pattern="^(manual|photo)$")
    
    @field_validator('systolic', 'diastolic')
    @classmethod
    def validate_pressure(cls, v):
        if v < 0:
            raise ValueError('Давление не может быть отрицательным')
        return v
```

### 13. Защита от XSS в шаблонах

**Проблема:** Нужно убедиться, что Jinja2 автоматически экранирует данные.

**Рекомендации:**
```python
# Убедиться что autoescape включен
templates = Jinja2Templates(
    directory="templates",
    autoescape=True  # По умолчанию включено, но лучше явно указать
)

# В шаблонах использовать фильтры
{{ user_input|e }}  # Экранирование HTML
{{ user_input|safe }}  # Только если доверяете источнику
```

### 14. Улучшение обработки ошибок

**Проблема:** Детальные сообщения об ошибках могут раскрывать внутреннюю структуру приложения.

**Рекомендации:**
```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", exc_info=exc)
    
    # В production не показывать детали ошибок
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Внутренняя ошибка сервера"}
        )
```

### 15. Аудит доступа к данным

**Рекомендации:**
```python
# Логирование всех операций с ПДн
async def get_patient(db: AsyncSession, patient_id: int, user_id: str):
    patient = await crud.get_patient(db, patient_id)
    
    # Аудит доступа
    logger.info(
        f"Access to patient data",
        extra={
            "user_id": user_id,
            "patient_id": patient_id,
            "action": "read",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    return patient
```

### 16. Шифрование данных в БД

**Рекомендации:**
- Использовать шифрование для чувствительных полей (ФИО, дата рождения)
- Использовать транзитное шифрование для подключения к БД
- Регулярно делать бэкапы с шифрованием

### 17. Защита от перечисления ресурсов

**Проблема:** Можно перебирать ID для доступа к чужим данным.

**Рекомендации:**
```python
# Использовать UUID вместо последовательных ID
# Или проверять права доступа перед возвратом данных
async def get_patient_detail(
    patient_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    patient = await crud.get_patient(db, patient_id)
    if not patient:
        # Всегда возвращать одинаковый ответ для несуществующих ресурсов
        raise HTTPException(status_code=404, detail="Пациент не найден")
    
    # Проверка прав доступа
    if not await has_access_to_patient(user_id, patient_id):
        raise HTTPException(status_code=404, detail="Пациент не найден")
    
    return patient
```

### 18. Валидация дат и времени

**Рекомендации:**
```python
from datetime import datetime, date
from pydantic import field_validator

class AppointmentCreateSchema(BaseModel):
    appointment_date: date
    appointment_time_start: str
    appointment_time_end: str
    
    @field_validator('appointment_date')
    @classmethod
    def validate_date(cls, v):
        if v < date.today():
            raise ValueError('Дата приёма не может быть в прошлом')
        if v > date.today().replace(year=date.today().year + 1):
            raise ValueError('Дата приёма слишком далеко в будущем')
        return v
    
    @field_validator('appointment_time_start', 'appointment_time_end')
    @classmethod
    def validate_time(cls, v):
        import re
        if not re.match(r'^\d{2}:\d{2}$', v):
            raise ValueError('Неверный формат времени')
        hour, minute = map(int, v.split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError('Неверное время')
        return v
```

## 📋 Чеклист безопасности

- [ ] Добавить аутентификацию и авторизацию
- [ ] Настроить CORS для production
- [ ] Добавить Rate Limiting
- [ ] Добавить CSRF защиту
- [ ] Улучшить валидацию файлов
- [ ] Добавить Security Headers
- [ ] Улучшить логирование (маскирование ПДн)
- [ ] Добавить валидацию всех входных данных
- [ ] Настроить HTTPS
- [ ] Добавить мониторинг безопасности
- [ ] Регулярные security аудиты
- [ ] Обновление зависимостей
- [ ] Настроить бэкапы с шифрованием
- [ ] Документировать политику безопасности

## 🔗 Полезные ресурсы

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security.html)

## 📝 Примечания

Этот документ должен регулярно обновляться по мере изменений в коде и появления новых угроз безопасности.


