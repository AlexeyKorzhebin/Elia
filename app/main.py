"""Главное приложение FastAPI"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.config import settings
from app.database import init_db, get_db
from app.api import patients, appointments, audio
from app import crud
from app.logger import setup_logging, get_logger
from app.middleware import LoggingMiddleware, ErrorLoggingMiddleware

# Настройка логирования
setup_logging(app_name="elia", log_level=settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle события приложения"""
    # Startup
    logger.info("Инициализация базы данных...")
    await init_db()
    
    # Инициализация тестовых данных из файла, если их нет в БД
    try:
        from app.database import async_session_maker
        async with async_session_maker() as db:
            test_data = await crud.get_test_data(db)
            if not test_data:
                # Пытаемся загрузить из файла
                talk_file_path = Path("data/talk.md")
                if talk_file_path.exists():
                    with open(talk_file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    await crud.create_or_update_test_data(db, content)
                    logger.info("Тестовые данные загружены из файла talk.md")
    except Exception as e:
        logger.warning(f"Не удалось инициализировать тестовые данные: {e}")
    
    logger.info(f"{settings.app_name} запущен!")
    
    yield
    
    # Shutdown
    logger.info(f"{settings.app_name} остановлен")


# Создание приложения
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="AI-платформа для врача - MVP",
    lifespan=lifespan
)

# Middleware для логирования (добавляем первым)
app.add_middleware(ErrorLoggingMiddleware)
app.add_middleware(LoggingMiddleware)

# CORS middleware (для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров API
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(audio.router)

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Шаблоны
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница приложения"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "version": settings.version
        }
    )


@app.get("/organization", response_class=HTMLResponse)
async def organization(request: Request):
    """Страница организации"""
    return templates.TemplateResponse(
        "organization.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "version": settings.version
        }
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Страница настроек"""
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "version": settings.version
        }
    )


@app.get("/support", response_class=HTMLResponse)
async def support(request: Request):
    """Страница поддержки"""
    return templates.TemplateResponse(
        "support.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "version": settings.version
        }
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """Страница о нас"""
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "version": settings.version
        }
    )


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version
    }


@app.get("/api/test-data")
async def get_test_data(db: AsyncSession = Depends(get_db)):
    """Получить тестовые данные (стенограмма)"""
    test_data = await crud.get_test_data(db)
    if test_data:
        return {"content": test_data.content}
    # Если данных нет, читаем из файла как fallback
    try:
        talk_file_path = Path("data/talk.md")
        if talk_file_path.exists():
            with open(talk_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content}
    except Exception as e:
        logger.error(f"Ошибка чтения файла talk.md: {e}")
    return {"content": ""}


@app.post("/api/test-data")
async def save_test_data(
    content: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """Сохранить тестовые данные (стенограмма)"""
    test_data = await crud.create_or_update_test_data(db, content)
    return {"success": True, "message": "Данные сохранены", "updated_at": test_data.updated_at}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

