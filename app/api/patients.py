"""API endpoints для работы с пациентами"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud
from app.schemas import PatientListSchema, DigitalPortraitSchema
from app.logger import get_logger

router = APIRouter(prefix="/api/patients", tags=["patients"])
logger = get_logger(__name__)


@router.get("", response_model=list[PatientListSchema])
async def get_patients_list(
    search: Optional[str] = Query(None, description="Поиск по ФИО"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Получить список пациентов"""
    logger.debug(f"Запрос списка пациентов: search={search}, skip={skip}, limit={limit}")
    try:
        patients = await crud.get_patients(db, search=search, skip=skip, limit=limit)
        logger.info(f"Получено {len(patients)} пациентов")
        return patients
    except Exception as e:
        logger.error(f"Ошибка при получении списка пациентов: {str(e)}")
        raise


@router.get("/{patient_id}", response_model=PatientListSchema)
async def get_patient_detail(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить детали пациента"""
    logger.debug(f"Запрос деталей пациента: patient_id={patient_id}")
    try:
        patient = await crud.get_patient(db, patient_id)
        if not patient:
            logger.warning(f"Пациент не найден: patient_id={patient_id}")
            raise HTTPException(status_code=404, detail="Пациент не найден")
        logger.info(f"Получены детали пациента: {patient.full_name} (ID: {patient_id})")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении пациента {patient_id}: {str(e)}")
        raise


@router.get("/{patient_id}/digital-portrait", response_model=DigitalPortraitSchema)
async def get_digital_portrait(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить цифровой портрет пациента"""
    logger.debug(f"Запрос цифрового портрета пациента: patient_id={patient_id}")
    try:
        patient = await crud.get_patient(db, patient_id)
        if not patient:
            logger.warning(f"Пациент не найден при запросе цифрового портрета: patient_id={patient_id}")
            raise HTTPException(status_code=404, detail="Пациент не найден")
        logger.info(f"Получен цифровой портрет пациента: {patient.full_name} (ID: {patient_id})")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении цифрового портрета пациента {patient_id}: {str(e)}")
        raise

