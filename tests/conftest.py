"""Конфигурация pytest и фикстуры"""
import pytest
import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import Patient, Appointment, GenderEnum, AppointmentStatus, MedicalReport, AudioFile
from datetime import date


# Тестовая база данных - используем отдельный файл
# Путь можно переопределить через переменную окружения TEST_DATABASE_PATH
TEST_DB_PATH = os.getenv("TEST_DATABASE_PATH", "elia-test.db")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

test_async_session = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Создать event loop для всех тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Глобальная переменная для хранения текущей сессии (для dependency override)
_current_session: AsyncSession | None = None


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override для dependency get_db - использует текущую сессию из фикстуры"""
    global _current_session
    if _current_session is None:
        async with test_async_session() as session:
            _current_session = session
            yield session
            _current_session = None
    else:
        yield _current_session


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Настройка тестовой БД перед всеми тестами"""
    # Проверяем, нужно ли очищать БД перед тестами
    # Можно установить CLEAN_TEST_DB=1 для очистки перед запуском
    clean_before = os.getenv("CLEAN_TEST_DB", "0") == "1"
    
    test_db_path = Path(TEST_DB_PATH)
    
    # Удаляем старую тестовую БД если нужно
    if clean_before and test_db_path.exists():
        test_db_path.unlink()
        print(f"🗑️  Удалена старая тестовая БД: {TEST_DB_PATH}")
    
    # Создаём таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print(f"✅ Тестовая БД инициализирована: {TEST_DB_PATH}")
    
    yield
    
    # Очищаем БД после всех тестов (опционально)
    # Можно установить CLEAN_TEST_DB_AFTER=1 для очистки после тестов
    clean_after = os.getenv("CLEAN_TEST_DB_AFTER", "0") == "1"
    if clean_after:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        if test_db_path.exists():
            test_db_path.unlink()
        print(f"🗑️  Тестовая БД очищена после тестов: {TEST_DB_PATH}")


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для получения тестовой сессии БД"""
    global _current_session
    
    # Используем сессию без автоматического отката
    # Изоляция обеспечивается через очистку данных в фикстуре clean_db
    async with test_async_session() as session:
        _current_session = session
        yield session
        _current_session = None


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для HTTP клиента"""
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def sample_patient(db_session: AsyncSession) -> Patient:
    """Создать тестового пациента"""
    patient = Patient(
        first_name="Иван",
        last_name="Иванов",
        middle_name="Петрович",
        date_of_birth=date(1980, 5, 15),
        gender=GenderEnum.MALE,
        medical_organization="ГБУЗ Поликлиника №1",
        medical_area="Терапевтический 5",
        last_visit_date=date(2025, 10, 20)
    )
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


@pytest.fixture(scope="function")
async def sample_appointment(db_session: AsyncSession, sample_patient: Patient) -> Appointment:
    """Создать тестовый приём"""
    appointment = Appointment(
        patient_id=sample_patient.id,
        appointment_date=date(2025, 10, 26),
        appointment_time_start="10:00",
        appointment_time_end="10:20",
        status=AppointmentStatus.SCHEDULED,
        is_active=False
    )
    db_session.add(appointment)
    await db_session.commit()
    await db_session.refresh(appointment)
    return appointment


@pytest.fixture(scope="function")
def temp_upload_dir(tmp_path):
    """Временная директория для загрузок"""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return upload_dir


@pytest.fixture(scope="function", autouse=False)
async def clean_db(db_session: AsyncSession):
    """Очистка БД перед тестом - удаляет все данные из таблиц
    Выполняется ПОСЛЕ создания фикстур (sample_patient и т.д.), но ПЕРЕД тестом
    """
    from sqlalchemy import text
    
    # Удаляем все записи в правильном порядке (с учётом внешних ключей)
    # Порядок важен из-за внешних ключей
    await db_session.execute(text("DELETE FROM medical_reports"))
    await db_session.execute(text("DELETE FROM audio_files"))
    await db_session.execute(text("DELETE FROM appointments"))
    await db_session.execute(text("DELETE FROM health_indicators"))
    await db_session.execute(text("DELETE FROM chronic_diseases"))
    await db_session.execute(text("DELETE FROM recent_diseases"))
    await db_session.execute(text("DELETE FROM patients"))
    await db_session.execute(text("DELETE FROM test_data"))
    await db_session.commit()
    yield

