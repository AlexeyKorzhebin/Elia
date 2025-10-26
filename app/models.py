"""SQLAlchemy модели"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, Date, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class GenderEnum(str, enum.Enum):
    """Пол пациента"""
    MALE = "male"
    FEMALE = "female"


class AppointmentStatus(str, enum.Enum):
    """Статус приёма"""
    SCHEDULED = "Запланирован"
    ANALYSIS = "Анализ"
    HEADACHE = "Головная боль"
    COLD = "ОРВИ"
    REFERRAL = "Направление на анализы"
    MONONUCLEOSIS = "Инфекционный мононуклеоз"
    ANEMIA = "Анемия"


class TranscriptionStatus(str, enum.Enum):
    """Статус транскрибации"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Patient(Base):
    """Модель пациента"""
    __tablename__ = "patients"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    middle_name: Mapped[str] = mapped_column(String(100))
    date_of_birth: Mapped[date] = mapped_column(Date)
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum))
    medical_organization: Mapped[str] = mapped_column(String(255))
    medical_area: Mapped[str] = mapped_column(String(50))
    last_visit_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chronic_diseases: Mapped[list["ChronicDisease"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    recent_diseases: Mapped[list["RecentDisease"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    health_indicators: Mapped[Optional["HealthIndicator"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        """Полное имя пациента"""
        return f"{self.last_name} {self.first_name} {self.middle_name}"
    
    @property
    def age(self) -> int:
        """Возраст пациента"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class ChronicDisease(Base):
    """Хронические заболевания"""
    __tablename__ = "chronic_diseases"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    name: Mapped[str] = mapped_column(String(255))
    
    patient: Mapped["Patient"] = relationship(back_populates="chronic_diseases")


class RecentDisease(Base):
    """Последние заболевания"""
    __tablename__ = "recent_diseases"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    name: Mapped[str] = mapped_column(String(255))
    
    patient: Mapped["Patient"] = relationship(back_populates="recent_diseases")


class HealthIndicator(Base):
    """Показатели здоровья"""
    __tablename__ = "health_indicators"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), unique=True)
    hemoglobin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # г/л
    cholesterol: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # ммоль/л
    bmi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # кг/м²
    heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # уд/мин
    
    patient: Mapped["Patient"] = relationship(back_populates="health_indicators")


class Appointment(Base):
    """Приём пациента"""
    __tablename__ = "appointments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    appointment_date: Mapped[date] = mapped_column(Date)
    appointment_time_start: Mapped[str] = mapped_column(String(5))  # HH:MM
    appointment_time_end: Mapped[str] = mapped_column(String(5))  # HH:MM
    status: Mapped[AppointmentStatus] = mapped_column(Enum(AppointmentStatus))
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient: Mapped["Patient"] = relationship(back_populates="appointments")
    medical_report: Mapped[Optional["MedicalReport"]] = relationship(back_populates="appointment", cascade="all, delete-orphan")
    audio_file: Mapped[Optional["AudioFile"]] = relationship(back_populates="appointment", cascade="all, delete-orphan")


class MedicalReport(Base):
    """Медицинский отчёт (анамнез)"""
    __tablename__ = "medical_reports"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"), unique=True)
    purpose: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Цель обращения
    complaints: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Жалобы пациента
    anamnesis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Анамнез
    submitted_to_mis: Mapped[bool] = mapped_column(default=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    appointment: Mapped["Appointment"] = relationship(back_populates="medical_report")


class AudioFile(Base):
    """Аудиофайл приёма"""
    __tablename__ = "audio_files"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"), unique=True)
    filename: Mapped[str] = mapped_column(String(255))
    filepath: Mapped[str] = mapped_column(String(512))
    file_size: Mapped[int] = mapped_column(Integer)  # bytes
    mime_type: Mapped[str] = mapped_column(String(50))
    transcription_status: Mapped[TranscriptionStatus] = mapped_column(
        Enum(TranscriptionStatus), 
        default=TranscriptionStatus.PENDING
    )
    transcription_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    transcribed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    appointment: Mapped["Appointment"] = relationship(back_populates="audio_file")

