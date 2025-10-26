"""Конфигурация pytest и фикстуры"""
import pytest
import asyncio
from pathlib import Path
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import Patient, Appointment, GenderEnum, AppointmentStatus
from datetime import date


# Тестовая база данных в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

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


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override для dependency get_db"""
    async with test_async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для получения тестовой сессии БД"""
    # Создаём таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with test_async_session() as session:
        yield session
    
    # Очищаем таблицы после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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

