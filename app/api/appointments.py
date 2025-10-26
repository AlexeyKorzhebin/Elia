"""API endpoints для работы с приёмами"""
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud
from app.schemas import (
    AppointmentListSchema,
    AppointmentDetailSchema,
    MedicalReportSchema,
    MedicalReportCreateUpdateSchema,
    MISSubmissionResponse
)

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.get("", response_model=list[AppointmentListSchema])
async def get_appointments_list(
    search: Optional[str] = Query(None, description="Поиск по ФИО пациента"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Получить список приёмов"""
    appointments = await crud.get_appointments(db, search=search, skip=skip, limit=limit)
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentDetailSchema)
async def get_appointment_detail(
    appointment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить детали приёма"""
    appointment = await crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Приём не найден")
    return appointment


@router.get("/{appointment_id}/report", response_model=MedicalReportSchema)
async def get_medical_report(
    appointment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить медицинский отчёт для приёма"""
    # Проверяем, существует ли приём
    appointment = await crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Приём не найден")
    
    report = await crud.get_medical_report(db, appointment_id)
    if not report:
        raise HTTPException(status_code=404, detail="Отчёт не найден")
    
    return report


@router.post("/{appointment_id}/report", response_model=MedicalReportSchema)
async def create_update_medical_report(
    appointment_id: int,
    report_data: MedicalReportCreateUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Создать или обновить медицинский отчёт"""
    # Проверяем, существует ли приём
    appointment = await crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Приём не найден")
    
    report = await crud.create_or_update_medical_report(
        db,
        appointment_id,
        purpose=report_data.purpose,
        complaints=report_data.complaints,
        anamnesis=report_data.anamnesis
    )
    
    return report


@router.post("/{appointment_id}/submit-to-mis", response_model=MISSubmissionResponse)
async def submit_to_mis(
    appointment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Имитация отправки отчёта в МИС"""
    # Проверяем, существует ли приём
    appointment = await crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Приём не найден")
    
    # Проверяем, существует ли отчёт
    report = await crud.get_medical_report(db, appointment_id)
    if not report:
        raise HTTPException(status_code=404, detail="Отчёт не найден. Сначала создайте отчёт.")
    
    # Имитация задержки отправки в МИС (3 секунды)
    await asyncio.sleep(3)
    
    # Обновляем статус отправки
    report = await crud.submit_report_to_mis(db, appointment_id)
    
    return MISSubmissionResponse(
        success=True,
        message="Отчёт успешно передан в МИС (MVP)",
        submitted_at=report.submitted_at
    )

