"""Pydantic схемы для валидации данных"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models import GenderEnum, AppointmentStatus, TranscriptionStatus


# === Patient Schemas ===

class ChronicDiseaseSchema(BaseModel):
    """Схема хронического заболевания"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str


class RecentDiseaseSchema(BaseModel):
    """Схема последнего заболевания"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str


class HealthIndicatorSchema(BaseModel):
    """Схема показателей здоровья"""
    model_config = ConfigDict(from_attributes=True)
    
    hemoglobin: Optional[float] = None
    cholesterol: Optional[float] = None
    bmi: Optional[float] = None
    heart_rate: Optional[int] = None


class PatientBaseSchema(BaseModel):
    """Базовая схема пациента"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    first_name: str
    last_name: str
    middle_name: str
    full_name: str
    age: int
    gender: GenderEnum
    date_of_birth: date


class PatientListSchema(PatientBaseSchema):
    """Схема пациента для списка"""
    pass


class DigitalPortraitSchema(PatientBaseSchema):
    """Схема цифрового портрета пациента"""
    medical_organization: str
    medical_area: str
    last_visit_date: Optional[date] = None
    chronic_diseases: list[ChronicDiseaseSchema] = []
    recent_diseases: list[RecentDiseaseSchema] = []
    health_indicators: Optional[HealthIndicatorSchema] = None


# === Appointment Schemas ===

class AppointmentBaseSchema(BaseModel):
    """Базовая схема приёма"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    appointment_date: date
    appointment_time_start: str
    appointment_time_end: str
    status: AppointmentStatus
    is_active: bool


class AppointmentListSchema(AppointmentBaseSchema):
    """Схема приёма для списка"""
    patient: PatientListSchema


class AppointmentDetailSchema(AppointmentBaseSchema):
    """Детальная схема приёма"""
    patient: PatientListSchema
    created_at: datetime


# === Medical Report Schemas ===

class MedicalReportSchema(BaseModel):
    """Схема медицинского отчёта"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    purpose: Optional[str] = None
    complaints: Optional[str] = None
    anamnesis: Optional[str] = None
    submitted_to_mis: bool
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class MedicalReportCreateUpdateSchema(BaseModel):
    """Схема для создания/обновления отчёта"""
    purpose: Optional[str] = None
    complaints: Optional[str] = None
    anamnesis: Optional[str] = None


class MISSubmissionResponse(BaseModel):
    """Ответ на отправку в МИС"""
    success: bool
    message: str
    submitted_at: datetime


# === Audio File Schemas ===

class AudioFileSchema(BaseModel):
    """Схема аудиофайла"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    filename: str
    file_size: int
    mime_type: str
    transcription_status: TranscriptionStatus
    transcription_text: Optional[str] = None
    uploaded_at: datetime
    transcribed_at: Optional[datetime] = None


class AudioUploadResponse(BaseModel):
    """Ответ на загрузку аудио"""
    id: int
    filename: str
    file_size: int
    message: str


class TranscriptionResponse(BaseModel):
    """Ответ на транскрибацию"""
    success: bool
    message: str
    transcription_status: TranscriptionStatus
    transcription_text: Optional[str] = None
    transcribed_at: Optional[datetime] = None


# === Generic Responses ===

class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""
    detail: str


class SuccessResponse(BaseModel):
    """Схема успешного ответа"""
    success: bool
    message: str

