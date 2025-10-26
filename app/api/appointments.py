"""API endpoints для работы с приёмами"""
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
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
from app.pdf_generator import generate_appointment_pdf
from app.logger import get_logger

router = APIRouter(prefix="/api/appointments", tags=["appointments"])
logger = get_logger(__name__)


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
    logger.info(f"Начало отправки отчёта в МИС для приёма: appointment_id={appointment_id}")
    
    try:
        # Проверяем, существует ли приём
        appointment = await crud.get_appointment(db, appointment_id)
        if not appointment:
            logger.warning(f"Попытка отправки в МИС несуществующего приёма: appointment_id={appointment_id}")
            raise HTTPException(status_code=404, detail="Приём не найден")
        
        # Проверяем, существует ли отчёт
        report = await crud.get_medical_report(db, appointment_id)
        if not report:
            logger.warning(f"Попытка отправки в МИС без отчёта: appointment_id={appointment_id}")
            raise HTTPException(status_code=404, detail="Отчёт не найден. Сначала создайте отчёт.")
        
        # Имитация задержки отправки в МИС (3 секунды)
        logger.debug(f"Отправка отчёта в МИС (симуляция 3 сек)...")
        await asyncio.sleep(3)
        
        # Обновляем статус отправки
        report = await crud.submit_report_to_mis(db, appointment_id)
        
        logger.info(f"Отчёт успешно отправлен в МИС: appointment_id={appointment_id}")
        
        return MISSubmissionResponse(
            success=True,
            message="Отчёт успешно передан в МИС (MVP)",
            submitted_at=report.submitted_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при отправке отчёта в МИС: appointment_id={appointment_id}, error={str(e)}")
        raise


@router.get("/{appointment_id}/download-pdf")
async def download_appointment_pdf(
    appointment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Скачать информацию о приёме в формате PDF"""
    logger.info(f"Запрос на скачивание PDF для приёма: appointment_id={appointment_id}")
    
    try:
        # Получаем данные о приёме
        appointment = await crud.get_appointment(db, appointment_id)
        if not appointment:
            logger.warning(f"Попытка скачать PDF несуществующего приёма: appointment_id={appointment_id}")
            raise HTTPException(status_code=404, detail="Приём не найден")
        
        # Получаем данные о пациенте
        patient = await crud.get_patient(db, appointment.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Пациент не найден")
        
        # Получаем медицинский отчёт (если есть)
        report = await crud.get_medical_report(db, appointment_id)
        
        # Формируем данные для PDF
        appointment_data = {
            'appointment_date': appointment.appointment_date.strftime('%d.%m.%Y'),
            'appointment_time_start': appointment.appointment_time_start,
            'appointment_time_end': appointment.appointment_time_end,
            'status': appointment.status.value if hasattr(appointment.status, 'value') else str(appointment.status),
        }
        
        patient_data = {
            'full_name': patient.full_name,
            'gender': patient.gender.value if hasattr(patient.gender, 'value') else str(patient.gender),
            'age': patient.age,
            'date_of_birth': patient.date_of_birth.strftime('%d.%m.%Y'),
            'medical_organization': patient.medical_organization,
            'medical_area': patient.medical_area,
            'chronic_diseases': [{'name': d.name} for d in patient.chronic_diseases],
            'recent_diseases': [{'name': d.name} for d in patient.recent_diseases],
            'health_indicators': {}
        }
        
        if patient.health_indicators:
            patient_data['health_indicators'] = {
                'hemoglobin': patient.health_indicators.hemoglobin,
                'cholesterol': patient.health_indicators.cholesterol,
                'bmi': patient.health_indicators.bmi,
                'heart_rate': patient.health_indicators.heart_rate,
            }
        
        report_data = None
        if report:
            report_data = {
                'purpose': report.purpose,
                'complaints': report.complaints,
                'anamnesis': report.anamnesis,
                'submitted_to_mis': report.submitted_to_mis,
                'submitted_at': report.submitted_at.strftime('%d.%m.%Y %H:%M') if report.submitted_at else None,
            }
    
        # Генерируем PDF
        logger.debug(f"Генерация PDF для приёма {appointment_id}...")
        pdf_buffer = generate_appointment_pdf(appointment_data, patient_data, report_data)
        
        # Формируем имя файла (транслитерация фамилии для совместимости)
        from urllib.parse import quote
        filename_base = f"priem_{appointment.appointment_date.strftime('%Y%m%d')}.pdf"
        filename_utf8 = f"priem_{patient.last_name}_{appointment.appointment_date.strftime('%Y%m%d')}.pdf"
        
        # RFC 5987 формат для поддержки кириллицы в именах файлов
        filename_encoded = quote(filename_utf8.encode('utf-8'))
        
        logger.info(f"PDF успешно сгенерирован: appointment_id={appointment_id}, filename={filename_utf8}")
        
        # Возвращаем PDF
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename_base}; filename*=UTF-8''{filename_encoded}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при генерации PDF: appointment_id={appointment_id}, error={str(e)}")
        raise

