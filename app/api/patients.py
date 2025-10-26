"""API endpoints для работы с пациентами"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud
from app.schemas import PatientListSchema, DigitalPortraitSchema

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("", response_model=list[PatientListSchema])
async def get_patients_list(
    search: Optional[str] = Query(None, description="Поиск по ФИО"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Получить список пациентов"""
    patients = await crud.get_patients(db, search=search, skip=skip, limit=limit)
    return patients


@router.get("/{patient_id}", response_model=PatientListSchema)
async def get_patient_detail(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить детали пациента"""
    patient = await crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return patient


@router.get("/{patient_id}/digital-portrait", response_model=DigitalPortraitSchema)
async def get_digital_portrait(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить цифровой портрет пациента"""
    patient = await crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return patient

