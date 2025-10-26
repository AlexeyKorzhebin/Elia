"""Тесты API endpoints"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO

from app.models import Patient, Appointment, MedicalReport, AudioFile


@pytest.mark.api
class TestPatientsAPI:
    """Тесты API пациентов"""
    
    async def test_get_patients_empty(self, client: AsyncClient):
        """Тест получения пустого списка пациентов"""
        response = await client.get("/api/patients")
        assert response.status_code == 200
        assert response.json() == []
    
    async def test_get_patients(self, client: AsyncClient, sample_patient: Patient):
        """Тест получения списка пациентов"""
        response = await client.get("/api/patients")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "Иван"
        assert data[0]["last_name"] == "Иванов"
    
    async def test_get_patient_detail(self, client: AsyncClient, sample_patient: Patient):
        """Тест получения деталей пациента"""
        response = await client.get(f"/api/patients/{sample_patient.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_patient.id
        assert data["first_name"] == "Иван"
    
    async def test_get_patient_not_found(self, client: AsyncClient):
        """Тест получения несуществующего пациента"""
        response = await client.get("/api/patients/999")
        assert response.status_code == 404
    
    async def test_get_digital_portrait(self, client: AsyncClient, sample_patient: Patient):
        """Тест получения цифрового портрета"""
        response = await client.get(f"/api/patients/{sample_patient.id}/digital-portrait")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_patient.id
        assert "chronic_diseases" in data
        assert "recent_diseases" in data
        assert "health_indicators" in data
    
    async def test_search_patients(self, client: AsyncClient, sample_patient: Patient):
        """Тест поиска пациентов"""
        response = await client.get("/api/patients?search=Иван")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Иван" in data[0]["first_name"]
        
        response = await client.get("/api/patients?search=Сидоров")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


@pytest.mark.api
class TestAppointmentsAPI:
    """Тесты API приёмов"""
    
    async def test_get_appointments_empty(self, client: AsyncClient):
        """Тест получения пустого списка приёмов"""
        response = await client.get("/api/appointments")
        assert response.status_code == 200
        assert response.json() == []
    
    async def test_get_appointments(self, client: AsyncClient, sample_appointment: Appointment):
        """Тест получения списка приёмов"""
        response = await client.get("/api/appointments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_appointment.id
        assert "patient" in data[0]
    
    async def test_get_appointment_detail(self, client: AsyncClient, sample_appointment: Appointment):
        """Тест получения деталей приёма"""
        response = await client.get(f"/api/appointments/{sample_appointment.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_appointment.id
        assert data["status"] == "Запланирован"
    
    async def test_get_appointment_not_found(self, client: AsyncClient):
        """Тест получения несуществующего приёма"""
        response = await client.get("/api/appointments/999")
        assert response.status_code == 404
    
    async def test_create_medical_report(self, client: AsyncClient, sample_appointment: Appointment):
        """Тест создания медицинского отчёта"""
        report_data = {
            "purpose": "Консультация терапевта",
            "complaints": "Головная боль, слабость",
            "anamnesis": "Симптомы появились 3 дня назад"
        }
        
        response = await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=report_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["purpose"] == report_data["purpose"]
        assert data["complaints"] == report_data["complaints"]
        assert data["submitted_to_mis"] == False
    
    async def test_update_medical_report(self, client: AsyncClient, sample_appointment: Appointment):
        """Тест обновления медицинского отчёта"""
        # Создаём отчёт
        report_data = {
            "purpose": "Консультация",
            "complaints": "Боль",
            "anamnesis": "История"
        }
        await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=report_data
        )
        
        # Обновляем отчёт
        updated_data = {
            "purpose": "Обновлённая цель",
            "complaints": "Боль",
            "anamnesis": "История"
        }
        response = await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=updated_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["purpose"] == "Обновлённая цель"
    
    async def test_get_medical_report(self, client: AsyncClient, sample_appointment: Appointment, db_session: AsyncSession):
        """Тест получения медицинского отчёта"""
        # Создаём отчёт
        report = MedicalReport(
            appointment_id=sample_appointment.id,
            purpose="Тест",
            complaints="Тест жалоб",
            anamnesis="Тест анамнеза"
        )
        db_session.add(report)
        await db_session.commit()
        
        response = await client.get(f"/api/appointments/{sample_appointment.id}/report")
        assert response.status_code == 200
        data = response.json()
        assert data["purpose"] == "Тест"
    
    async def test_get_medical_report_not_found(self, client: AsyncClient, sample_appointment: Appointment):
        """Тест получения несуществующего отчёта"""
        response = await client.get(f"/api/appointments/{sample_appointment.id}/report")
        assert response.status_code == 404
    
    async def test_submit_to_mis(self, client: AsyncClient, sample_appointment: Appointment, db_session: AsyncSession):
        """Тест отправки отчёта в МИС"""
        # Создаём отчёт
        report = MedicalReport(
            appointment_id=sample_appointment.id,
            purpose="Тест",
            complaints="Тест",
            anamnesis="Тест"
        )
        db_session.add(report)
        await db_session.commit()
        
        response = await client.post(f"/api/appointments/{sample_appointment.id}/submit-to-mis")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Отчёт успешно передан в МИС" in data["message"]
        assert "submitted_at" in data
    
    async def test_submit_to_mis_no_report(self, client: AsyncClient, sample_appointment: Appointment):
        """Тест отправки в МИС без отчёта"""
        response = await client.post(f"/api/appointments/{sample_appointment.id}/submit-to-mis")
        assert response.status_code == 404


@pytest.mark.api
class TestAudioAPI:
    """Тесты API аудиофайлов"""
    
    async def test_upload_audio(self, client: AsyncClient, sample_appointment: Appointment):
        """Тест загрузки аудиофайла"""
        # Создаём фиктивный аудиофайл
        audio_content = b"fake audio content"
        files = {
            "file": ("test_audio.mp3", BytesIO(audio_content), "audio/mpeg")
        }
        
        response = await client.post(
            f"/api/audio/upload?appointment_id={sample_appointment.id}",
            files=files
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["filename"] == "test_audio.mp3"
        assert "Аудиофайл успешно загружен" in data["message"]
    
    async def test_upload_audio_invalid_appointment(self, client: AsyncClient):
        """Тест загрузки аудио для несуществующего приёма"""
        audio_content = b"fake audio content"
        files = {
            "file": ("test_audio.mp3", BytesIO(audio_content), "audio/mpeg")
        }
        
        response = await client.post(
            "/api/audio/upload?appointment_id=999",
            files=files
        )
        assert response.status_code == 404
    
    async def test_upload_audio_duplicate(self, client: AsyncClient, sample_appointment: Appointment, db_session: AsyncSession):
        """Тест загрузки дублирующего аудиофайла"""
        # Создаём первый аудиофайл
        audio = AudioFile(
            appointment_id=sample_appointment.id,
            filename="existing.mp3",
            filepath="/tmp/existing.mp3",
            file_size=1000,
            mime_type="audio/mpeg"
        )
        db_session.add(audio)
        await db_session.commit()
        
        # Пытаемся загрузить второй
        audio_content = b"fake audio content"
        files = {
            "file": ("test_audio.mp3", BytesIO(audio_content), "audio/mpeg")
        }
        
        response = await client.post(
            f"/api/audio/upload?appointment_id={sample_appointment.id}",
            files=files
        )
        assert response.status_code == 400
    
    async def test_get_audio_info(self, client: AsyncClient, sample_appointment: Appointment, db_session: AsyncSession):
        """Тест получения информации об аудиофайле"""
        audio = AudioFile(
            appointment_id=sample_appointment.id,
            filename="test.mp3",
            filepath="/tmp/test.mp3",
            file_size=5000,
            mime_type="audio/mpeg"
        )
        db_session.add(audio)
        await db_session.commit()
        await db_session.refresh(audio)
        
        response = await client.get(f"/api/audio/{audio.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == audio.id
        assert data["filename"] == "test.mp3"
        assert data["transcription_status"] == "pending"
    
    async def test_get_audio_not_found(self, client: AsyncClient):
        """Тест получения несуществующего аудиофайла"""
        response = await client.get("/api/audio/999")
        assert response.status_code == 404
    
    async def test_transcribe_audio(self, client: AsyncClient, sample_appointment: Appointment, db_session: AsyncSession):
        """Тест транскрибации аудиофайла"""
        audio = AudioFile(
            appointment_id=sample_appointment.id,
            filename="test.mp3",
            filepath="/tmp/test.mp3",
            file_size=5000,
            mime_type="audio/mpeg"
        )
        db_session.add(audio)
        await db_session.commit()
        await db_session.refresh(audio)
        
        response = await client.post(f"/api/audio/{audio.id}/transcribe")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Транскрибация завершена" in data["message"]
        assert data["transcription_status"] == "completed"
        assert data["transcription_text"] is not None
        assert len(data["transcription_text"]) > 0
    
    async def test_transcribe_audio_not_found(self, client: AsyncClient):
        """Тест транскрибации несуществующего аудиофайла"""
        response = await client.post("/api/audio/999/transcribe")
        assert response.status_code == 404


@pytest.mark.api
class TestHealthCheck:
    """Тесты системных endpoints"""
    
    async def test_health_check(self, client: AsyncClient):
        """Тест health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "app" in data
        assert "version" in data
    
    async def test_root(self, client: AsyncClient):
        """Тест главной страницы"""
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

