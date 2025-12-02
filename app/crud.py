"""CRUD операции для работы с базой данных"""
from datetime import datetime
from typing import Optional, Sequence
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Patient, Appointment, MedicalReport, AudioFile,
    ChronicDisease, RecentDisease, HealthIndicator,
    TranscriptionStatus
)


# === Patient CRUD ===

async def get_patient(db: AsyncSession, patient_id: int) -> Optional[Patient]:
    """Получить пациента по ID"""
    result = await db.execute(
        select(Patient)
        .options(
            selectinload(Patient.chronic_diseases),
            selectinload(Patient.recent_diseases),
            selectinload(Patient.health_indicators)
        )
        .where(Patient.id == patient_id)
    )
    return result.scalar_one_or_none()


async def get_patients(
    db: AsyncSession, 
    search: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 100
) -> Sequence[Patient]:
    """Получить список пациентов с возможностью поиска"""
    query = select(Patient)
    
    if search:
        search_filter = or_(
            Patient.first_name.ilike(f"%{search}%"),
            Patient.last_name.ilike(f"%{search}%"),
            Patient.middle_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# === Appointment CRUD ===

async def get_appointment(db: AsyncSession, appointment_id: int) -> Optional[Appointment]:
    """Получить приём по ID"""
    result = await db.execute(
        select(Appointment)
        .options(selectinload(Appointment.patient))
        .where(Appointment.id == appointment_id)
    )
    return result.scalar_one_or_none()


async def get_appointments(
    db: AsyncSession,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Sequence[Appointment]:
    """Получить список приёмов с пациентами"""
    query = select(Appointment).options(selectinload(Appointment.patient))
    
    if search:
        query = query.join(Patient).where(
            or_(
                Patient.first_name.ilike(f"%{search}%"),
                Patient.last_name.ilike(f"%{search}%"),
                Patient.middle_name.ilike(f"%{search}%")
            )
        )
    
    query = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time_start.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


# === Medical Report CRUD ===

async def get_medical_report(db: AsyncSession, appointment_id: int) -> Optional[MedicalReport]:
    """Получить медицинский отчёт для приёма"""
    result = await db.execute(
        select(MedicalReport).where(MedicalReport.appointment_id == appointment_id)
    )
    return result.scalar_one_or_none()


async def create_or_update_medical_report(
    db: AsyncSession,
    appointment_id: int,
    purpose: Optional[str] = None,
    complaints: Optional[str] = None,
    anamnesis: Optional[str] = None
) -> MedicalReport:
    """Создать или обновить медицинский отчёт"""
    report = await get_medical_report(db, appointment_id)
    
    if report:
        # Обновление существующего отчёта
        if purpose is not None:
            report.purpose = purpose
        if complaints is not None:
            report.complaints = complaints
        if anamnesis is not None:
            report.anamnesis = anamnesis
        report.updated_at = datetime.utcnow()
    else:
        # Создание нового отчёта
        report = MedicalReport(
            appointment_id=appointment_id,
            purpose=purpose,
            complaints=complaints,
            anamnesis=anamnesis
        )
        db.add(report)
    
    await db.commit()
    await db.refresh(report)
    return report


async def submit_report_to_mis(db: AsyncSession, appointment_id: int) -> MedicalReport:
    """Имитация отправки отчёта в МИС"""
    report = await get_medical_report(db, appointment_id)
    if not report:
        raise ValueError("Отчёт не найден")
    
    report.submitted_to_mis = True
    report.submitted_at = datetime.utcnow()
    await db.commit()
    await db.refresh(report)
    return report


# === Audio File CRUD ===

async def get_audio_file(db: AsyncSession, audio_id: int) -> Optional[AudioFile]:
    """Получить аудиофайл по ID"""
    result = await db.execute(
        select(AudioFile).where(AudioFile.id == audio_id)
    )
    return result.scalar_one_or_none()


async def get_audio_file_by_appointment(db: AsyncSession, appointment_id: int) -> Optional[AudioFile]:
    """Получить аудиофайл для приёма"""
    result = await db.execute(
        select(AudioFile).where(AudioFile.appointment_id == appointment_id)
    )
    return result.scalar_one_or_none()


async def create_audio_file(
    db: AsyncSession,
    appointment_id: int,
    filename: str,
    filepath: str,
    file_size: int,
    mime_type: str
) -> AudioFile:
    """Создать запись об аудиофайле"""
    audio = AudioFile(
        appointment_id=appointment_id,
        filename=filename,
        filepath=filepath,
        file_size=file_size,
        mime_type=mime_type,
        transcription_status=TranscriptionStatus.PENDING
    )
    db.add(audio)
    await db.commit()
    await db.refresh(audio)
    return audio


async def update_transcription(
    db: AsyncSession,
    audio_id: int,
    status: TranscriptionStatus,
    text: Optional[str] = None
) -> AudioFile:
    """Обновить статус транскрибации"""
    audio = await get_audio_file(db, audio_id)
    if not audio:
        raise ValueError("Аудиофайл не найден")
    
    audio.transcription_status = status
    if text:
        audio.transcription_text = text
    if status == TranscriptionStatus.COMPLETED:
        audio.transcribed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(audio)
    return audio


async def delete_audio_file(db: AsyncSession, audio_id: int) -> None:
    """Удалить аудиофайл"""
    audio = await get_audio_file(db, audio_id)
    if not audio:
        raise ValueError("Аудиофайл не найден")
    
    await db.delete(audio)
    await db.commit()


# === Health Indicators CRUD ===

async def get_health_indicators(db: AsyncSession, patient_id: int) -> Optional[HealthIndicator]:
    """Получить показатели здоровья пациента"""
    result = await db.execute(
        select(HealthIndicator).where(HealthIndicator.patient_id == patient_id)
    )
    return result.scalar_one_or_none()


async def update_blood_pressure(
    db: AsyncSession,
    patient_id: int,
    systolic: int,
    diastolic: int,
    pulse: Optional[int] = None,
    source: str = "manual"
) -> HealthIndicator:
    """Обновить показатели давления пациента"""
    indicators = await get_health_indicators(db, patient_id)
    
    if not indicators:
        # Создаём новую запись
        indicators = HealthIndicator(
            patient_id=patient_id,
            systolic_pressure=systolic,
            diastolic_pressure=diastolic,
            pulse=pulse,
            bp_source=source,
            bp_updated_at=datetime.utcnow()
        )
        db.add(indicators)
    else:
        # Обновляем существующую
        indicators.systolic_pressure = systolic
        indicators.diastolic_pressure = diastolic
        if pulse is not None:
            indicators.pulse = pulse
        indicators.bp_source = source
        indicators.bp_updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(indicators)
    return indicators

