"""
Быстрые тесты для проверки работоспособности приложения
Можно запускать отдельно: pytest tests/test_quick_check.py -v
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Patient, Appointment
from tests.test_data import (
    get_test_transcription,
    get_test_medical_report
)


@pytest.mark.api
class TestQuickCheck:
    """Быстрые тесты для проверки работоспособности"""
    
    async def test_health_check(self, client: AsyncClient):
        """Проверка health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "app" in data
        assert "version" in data
    
    async def test_appointments_exist(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Проверка наличия приёмов"""
        response = await client.get("/api/appointments")
        assert response.status_code == 200
        appointments = response.json()
        assert len(appointments) > 0
        assert any(a["id"] == sample_appointment.id for a in appointments)
    
    async def test_patients_exist(
        self,
        client: AsyncClient,
        sample_patient: Patient
    ):
        """Проверка наличия пациентов"""
        response = await client.get("/api/patients")
        assert response.status_code == 200
        patients = response.json()
        assert len(patients) > 0
        assert any(p["id"] == sample_patient.id for p in patients)
    
    async def test_transcription_update_quick(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Быстрый тест обновления транскрипции"""
        # Получаем аудиофайл
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        
        if response.status_code != 200:
            pytest.skip("Аудиофайл не найден")
        
        audio_id = response.json()["id"]
        transcription = get_test_transcription("short")
        
        response = await client.put(
            f"/api/audio/{audio_id}/transcription",
            json={"transcription_text": transcription}
        )
        
        assert response.status_code == 200
        assert response.json()["transcription_status"] == "completed"
    
    async def test_medical_report_quick(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Быстрый тест сохранения медицинского отчёта"""
        report_data = get_test_medical_report(1)
        
        response = await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=report_data
        )
        
        assert response.status_code == 200
        assert response.json()["purpose"] == report_data["purpose"]
    
    async def test_pdf_generation_quick(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Быстрый тест генерации PDF"""
        # Создаём отчёт для полноты данных
        report_data = get_test_medical_report(1)
        await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=report_data
        )
        
        response = await client.get(
            f"/api/appointments/{sample_appointment.id}/download-pdf"
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0

