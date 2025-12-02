"""API endpoints для работы с пациентами"""
import base64
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app import crud
from app.schemas import PatientListSchema, DigitalPortraitSchema, HealthIndicatorSchema
from app.openai_service import openai_service
from app.logger import get_logger

router = APIRouter(prefix="/api/patients", tags=["patients"])
logger = get_logger(__name__)


class TonometerRecognitionResponse(BaseModel):
    """Ответ на распознавание тонометра"""
    success: bool
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    pulse: Optional[int] = None
    confidence: Optional[str] = None
    error: Optional[str] = None


class BloodPressureUpdateRequest(BaseModel):
    """Запрос на обновление показателей давления"""
    systolic: int
    diastolic: int
    pulse: Optional[int] = None
    source: str = "manual"


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


@router.post("/{patient_id}/recognize-tonometer", response_model=TonometerRecognitionResponse)
async def recognize_tonometer(
    patient_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Распознать показатели с фотографии тонометра через OpenAI Vision
    """
    logger.info(f"Запрос распознавания тонометра для пациента: patient_id={patient_id}")
    
    # Проверяем существование пациента
    patient = await crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    
    # Проверяем тип файла
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/heic", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый формат изображения. Допустимые: {', '.join(allowed_types)}"
        )
    
    try:
        # Читаем файл и конвертируем в base64
        file_content = await file.read()
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Распознаём через OpenAI Vision
        result = await openai_service.recognize_tonometer_reading(image_base64)
        
        logger.info(f"Результат распознавания: {result}")
        
        return TonometerRecognitionResponse(
            success=result.get("success", False),
            systolic=result.get("systolic"),
            diastolic=result.get("diastolic"),
            pulse=result.get("pulse"),
            confidence=result.get("confidence"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Ошибка при распознавании тонометра: {str(e)}")
        return TonometerRecognitionResponse(
            success=False,
            error=f"Ошибка распознавания: {str(e)}"
        )


@router.post("/{patient_id}/blood-pressure", response_model=HealthIndicatorSchema)
async def update_blood_pressure(
    patient_id: int,
    data: BloodPressureUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Сохранить показатели давления пациента
    """
    logger.info(f"Обновление показателей давления для пациента: patient_id={patient_id}, data={data}")
    
    # Проверяем существование пациента
    patient = await crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    
    # Валидация значений
    if not (60 <= data.systolic <= 300):
        raise HTTPException(status_code=400, detail="Систолическое давление должно быть от 60 до 300")
    if not (30 <= data.diastolic <= 200):
        raise HTTPException(status_code=400, detail="Диастолическое давление должно быть от 30 до 200")
    if data.pulse is not None and not (30 <= data.pulse <= 250):
        raise HTTPException(status_code=400, detail="Пульс должен быть от 30 до 250")
    
    try:
        indicators = await crud.update_blood_pressure(
            db,
            patient_id=patient_id,
            systolic=data.systolic,
            diastolic=data.diastolic,
            pulse=data.pulse,
            source=data.source
        )
        
        logger.info(f"Показатели давления обновлены: patient_id={patient_id}")
        
        return indicators
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении давления: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения: {str(e)}")

