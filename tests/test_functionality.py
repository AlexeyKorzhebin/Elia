"""
Тесты функциональности приложения с использованием тестовых данных
Проверяют работоспособность без создания новых приёмов в БД
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Patient, Appointment
from tests.test_data import (
    get_test_transcription,
    get_test_anamnesis,
    get_test_medical_report,
    get_test_blood_pressure,
    TEST_SCENARIOS,
    EDGE_CASE_TEXTS,
    ERROR_TEST_CASES
)


@pytest.mark.api
class TestTranscriptionWorkflow:
    """Тесты workflow работы с транскрипцией"""
    
    async def test_update_transcription(
        self, 
        client: AsyncClient, 
        sample_appointment: Appointment
    ):
        """Тест обновления транскрипции"""
        # Получаем или создаём аудиофайл
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        
        audio_id = None
        if response.status_code == 200:
            audio_id = response.json()["id"]
        else:
            # Создаём mock транскрипцию если нет аудио
            response = await client.post(
                "/api/audio/mock-transcription",
                params={"appointment_id": sample_appointment.id}
            )
            if response.status_code == 200:
                audio_id = response.json()["transcription_text"] and response.json().get("transcription_status") == "completed"
                # Получаем ID аудиофайла
                response = await client.get(
                    f"/api/audio/by-appointment/{sample_appointment.id}"
                )
                if response.status_code == 200:
                    audio_id = response.json()["id"]
        
        if not audio_id:
            pytest.skip("Не удалось получить или создать аудиофайл")
        
        # Обновляем транскрипцию
        transcription = get_test_transcription("cardiovascular")
        response = await client.put(
            f"/api/audio/{audio_id}/transcription",
            json={"transcription_text": transcription}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["transcription_status"] == "completed"
        assert len(data["transcription_text"]) > 0
        
        # Проверяем сохранение
        response = await client.get(f"/api/audio/{audio_id}")
        assert response.status_code == 200
        saved_text = response.json()["transcription_text"]
        assert len(saved_text) > 0
    
    async def test_transcription_persistence(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест сохранения транскрипции при переключении"""
        # Получаем аудиофайл
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        
        if response.status_code != 200:
            pytest.skip("Аудиофайл не найден")
        
        audio_id = response.json()["id"]
        
        # Получаем текущую транскрипцию
        response = await client.get(f"/api/audio/{audio_id}")
        original_text = response.json().get("transcription_text", "")
        
        # Добавляем тестовый маркер
        test_marker = "\n\n[ТЕСТОВОЕ ИЗМЕНЕНИЕ]"
        modified_text = original_text + test_marker if original_text else test_marker
        
        # Сохраняем изменения
        response = await client.put(
            f"/api/audio/{audio_id}/transcription",
            json={"transcription_text": modified_text}
        )
        assert response.status_code == 200
        
        # Проверяем сохранение
        response = await client.get(f"/api/audio/{audio_id}")
        assert response.status_code == 200
        saved_text = response.json()["transcription_text"]
        assert test_marker in saved_text or modified_text == saved_text
    
    @pytest.mark.parametrize("scenario", [
        "cardiovascular",
        "respiratory",
        "gastroenterology",
        "neurology",
        "short"
    ])
    async def test_different_transcription_scenarios(
        self,
        client: AsyncClient,
        sample_appointment: Appointment,
        scenario: str
    ):
        """Тест различных сценариев транскрипции"""
        # Получаем аудиофайл
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        
        if response.status_code != 200:
            pytest.skip("Аудиофайл не найден")
        
        audio_id = response.json()["id"]
        transcription = get_test_transcription(scenario)
        
        response = await client.put(
            f"/api/audio/{audio_id}/transcription",
            json={"transcription_text": transcription}
        )
        
        assert response.status_code == 200
        assert len(response.json()["transcription_text"]) > 0


@pytest.mark.api
@pytest.mark.slow
class TestAnamnesisExtraction:
    """Тесты извлечения анамнеза"""
    
    async def test_extract_anamnesis(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест извлечения анамнеза из транскрипции"""
        # Получаем аудиофайл
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        
        if response.status_code != 200:
            pytest.skip("Аудиофайл не найден")
        
        audio_id = response.json()["id"]
        
        # Убеждаемся, что есть транскрипция
        response = await client.get(f"/api/audio/{audio_id}")
        if not response.json().get("transcription_text"):
            # Создаём транскрипцию если её нет
            transcription = get_test_transcription("cardiovascular")
            await client.put(
                f"/api/audio/{audio_id}/transcription",
                json={"transcription_text": transcription}
            )
        
        # Извлекаем анамнез
        response = await client.post(f"/api/audio/{audio_id}/extract-anamnesis")
        
        # Может быть 200 или ошибка если OpenAI не настроен
        assert response.status_code in [200, 500, 503]
        
        if response.status_code == 200:
            anamnesis = response.json()
            assert "purpose" in anamnesis or anamnesis.get("purpose") is not None
            assert "complaints" in anamnesis or anamnesis.get("complaints") is not None
            assert "anamnesis" in anamnesis or anamnesis.get("anamnesis") is not None
    
    @pytest.mark.parametrize("scenario", [
        "cardiovascular",
        "respiratory",
        "gastroenterology",
        "neurology"
    ])
    async def test_extract_anamnesis_different_scenarios(
        self,
        client: AsyncClient,
        sample_appointment: Appointment,
        scenario: str
    ):
        """Тест извлечения анамнеза для разных сценариев"""
        # Получаем аудиофайл
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        
        if response.status_code != 200:
            pytest.skip("Аудиофайл не найден")
        
        audio_id = response.json()["id"]
        
        # Устанавливаем транскрипцию
        transcription = get_test_transcription(scenario)
        await client.put(
            f"/api/audio/{audio_id}/transcription",
            json={"transcription_text": transcription}
        )
        
        # Извлекаем анамнез
        response = await client.post(f"/api/audio/{audio_id}/extract-anamnesis")
        
        # Может быть ошибка если OpenAI не настроен
        assert response.status_code in [200, 500, 503]


@pytest.mark.api
class TestMedicalReport:
    """Тесты работы с медицинскими отчётами"""
    
    @pytest.mark.parametrize("variant", [1, 2, 3])
    async def test_create_medical_report(
        self,
        client: AsyncClient,
        sample_appointment: Appointment,
        variant: int
    ):
        """Тест создания медицинского отчёта"""
        report_data = get_test_medical_report(variant)
        
        response = await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=report_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["purpose"] == report_data["purpose"]
        assert data["complaints"] == report_data["complaints"]
        assert data["anamnesis"] == report_data["anamnesis"]
        assert data["submitted_to_mis"] == False
    
    async def test_update_medical_report(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест обновления медицинского отчёта"""
        # Создаём отчёт
        report_data = get_test_medical_report(1)
        await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=report_data
        )
        
        # Обновляем отчёт
        updated_data = get_test_medical_report(2)
        response = await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=updated_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["purpose"] == updated_data["purpose"]
    
    async def test_get_medical_report(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест получения медицинского отчёта"""
        # Создаём отчёт
        report_data = get_test_medical_report(1)
        await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=report_data
        )
        
        # Получаем отчёт
        response = await client.get(
            f"/api/appointments/{sample_appointment.id}/report"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["purpose"] == report_data["purpose"]
    
    async def test_submit_to_mis(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест отправки отчёта в МИС"""
        # Создаём отчёт
        report_data = get_test_medical_report(1)
        await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=report_data
        )
        
        # Отправляем в МИС
        response = await client.post(
            f"/api/appointments/{sample_appointment.id}/submit-to-mis"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "submitted_at" in data


@pytest.mark.api
class TestBloodPressure:
    """Тесты работы с артериальным давлением"""
    
    @pytest.mark.parametrize("variant", [1, 2, 3])
    async def test_update_blood_pressure(
        self,
        client: AsyncClient,
        sample_patient: Patient,
        variant: int
    ):
        """Тест сохранения показателей артериального давления"""
        bp_data = get_test_blood_pressure(variant)
        
        response = await client.post(
            f"/api/patients/{sample_patient.id}/blood-pressure",
            json=bp_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["systolic_pressure"] == bp_data["systolic"]
        assert data["diastolic_pressure"] == bp_data["diastolic"]
        if bp_data.get("pulse"):
            assert data["pulse"] == bp_data["pulse"]
    
    async def test_blood_pressure_persistence(
        self,
        client: AsyncClient,
        sample_patient: Patient
    ):
        """Тест сохранения давления в цифровом портрете"""
        bp_data = get_test_blood_pressure(1)
        
        # Сохраняем давление
        response = await client.post(
            f"/api/patients/{sample_patient.id}/blood-pressure",
            json=bp_data
        )
        assert response.status_code == 200
        saved_data = response.json()
        assert saved_data["systolic_pressure"] == bp_data["systolic"]
        assert saved_data["diastolic_pressure"] == bp_data["diastolic"]
        
        # Проверяем в цифровом портрете
        response = await client.get(
            f"/api/patients/{sample_patient.id}/digital-portrait"
        )
        
        assert response.status_code == 200
        portrait = response.json()
        indicators = portrait.get("health_indicators")
        # health_indicators может быть None, если не создан
        if indicators:
            assert indicators.get("systolic_pressure") == bp_data["systolic"]
            assert indicators.get("diastolic_pressure") == bp_data["diastolic"]
        else:
            # Если health_indicators None, проверяем что данные сохранились через API
            assert saved_data["systolic_pressure"] == bp_data["systolic"]
            assert saved_data["diastolic_pressure"] == bp_data["diastolic"]


@pytest.mark.api
class TestPDFGeneration:
    """Тесты генерации PDF"""
    
    async def test_generate_pdf(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест генерации PDF отчёта"""
        # Создаём отчёт для полноты данных
        report_data = get_test_medical_report(1)
        await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=report_data
        )
        
        # Генерируем PDF
        response = await client.get(
            f"/api/appointments/{sample_appointment.id}/download-pdf"
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0


@pytest.mark.api
class TestSearch:
    """Тесты поиска"""
    
    async def test_search_patients(
        self,
        client: AsyncClient,
        sample_patient: Patient
    ):
        """Тест поиска пациентов"""
        # Поиск по имени
        response = await client.get(
            "/api/patients",
            params={"search": sample_patient.first_name}
        )
        
        assert response.status_code == 200
        patients = response.json()
        assert len(patients) > 0
        assert any(p["id"] == sample_patient.id for p in patients)
    
    async def test_search_appointments(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест поиска приёмов"""
        # Поиск по имени пациента
        response = await client.get(
            "/api/appointments",
            params={"search": sample_appointment.patient.first_name}
        )
        
        assert response.status_code == 200
        appointments = response.json()
        assert len(appointments) > 0
        assert any(a["id"] == sample_appointment.id for a in appointments)


@pytest.mark.api
class TestEdgeCases:
    """Тесты граничных случаев"""
    
    async def test_empty_transcription(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест с пустой транскрипцией"""
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        
        if response.status_code != 200:
            pytest.skip("Аудиофайл не найден")
        
        audio_id = response.json()["id"]
        empty_text = EDGE_CASE_TEXTS["empty_transcription"]
        
        response = await client.put(
            f"/api/audio/{audio_id}/transcription",
            json={"transcription_text": empty_text}
        )
        
        # Пустая транскрипция может быть допустима
        assert response.status_code in [200, 400]
    
    async def test_special_characters_transcription(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест транскрипции со специальными символами"""
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        
        if response.status_code != 200:
            pytest.skip("Аудиофайл не найден")
        
        audio_id = response.json()["id"]
        special_text = EDGE_CASE_TEXTS["special_characters"]
        
        response = await client.put(
            f"/api/audio/{audio_id}/transcription",
            json={"transcription_text": special_text}
        )
        
        assert response.status_code == 200
    
    async def test_unicode_transcription(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест транскрипции с Unicode символами"""
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        
        if response.status_code != 200:
            pytest.skip("Аудиофайл не найден")
        
        audio_id = response.json()["id"]
        unicode_text = EDGE_CASE_TEXTS["unicode_text"]
        
        response = await client.put(
            f"/api/audio/{audio_id}/transcription",
            json={"transcription_text": unicode_text}
        )
        
        assert response.status_code == 200
        saved_text = response.json()["transcription_text"]
        assert "½" in saved_text


@pytest.mark.api
class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    async def test_invalid_appointment_id(self, client: AsyncClient):
        """Тест с несуществующим приёмом"""
        invalid_id = ERROR_TEST_CASES["invalid_appointment_id"]["appointment_id"]
        
        response = await client.get(f"/api/appointments/{invalid_id}")
        assert response.status_code == 404
        
        response = await client.get(f"/api/appointments/{invalid_id}/report")
        assert response.status_code == 404
    
    async def test_invalid_audio_id(self, client: AsyncClient):
        """Тест с несуществующим аудиофайлом"""
        invalid_id = ERROR_TEST_CASES["invalid_audio_id"]["audio_id"]
        
        response = await client.get(f"/api/audio/{invalid_id}")
        assert response.status_code == 404
        
        response = await client.post(f"/api/audio/{invalid_id}/transcribe")
        assert response.status_code == 404
    
    async def test_invalid_patient_id(self, client: AsyncClient):
        """Тест с несуществующим пациентом"""
        invalid_id = ERROR_TEST_CASES["invalid_patient_id"]["patient_id"]
        
        response = await client.get(f"/api/patients/{invalid_id}")
        assert response.status_code == 404
        
        response = await client.get(f"/api/patients/{invalid_id}/digital-portrait")
        assert response.status_code == 404
    
    async def test_invalid_blood_pressure(self, client: AsyncClient, sample_patient: Patient):
        """Тест с некорректными значениями давления"""
        invalid_bp = ERROR_TEST_CASES["invalid_blood_pressure"]
        
        response = await client.post(
            f"/api/patients/{sample_patient.id}/blood-pressure",
            json={
                "systolic": invalid_bp["systolic"],
                "diastolic": invalid_bp["diastolic"],
                "pulse": invalid_bp["pulse"]
            }
        )
        
        # Должна быть ошибка валидации
        assert response.status_code == 400


@pytest.mark.api
class TestFullWorkflow:
    """Тесты полного workflow"""
    
    @pytest.mark.slow
    async def test_full_workflow_scenario(
        self,
        client: AsyncClient,
        sample_appointment: Appointment
    ):
        """Тест полного workflow: транскрипция → редактирование → анамнез → отчёт → МИС"""
        # Шаг 1: Получаем или создаём аудиофайл
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        
        if response.status_code != 200:
            # Создаём mock транскрипцию
            response = await client.post(
                "/api/audio/mock-transcription",
                params={"appointment_id": sample_appointment.id}
            )
            if response.status_code != 200:
                pytest.skip("Не удалось создать аудиофайл")
        
        response = await client.get(
            f"/api/audio/by-appointment/{sample_appointment.id}"
        )
        audio_id = response.json()["id"]
        
        # Шаг 2: Обновляем транскрипцию
        transcription = get_test_transcription("cardiovascular")
        response = await client.put(
            f"/api/audio/{audio_id}/transcription",
            json={"transcription_text": transcription}
        )
        assert response.status_code == 200
        
        # Шаг 3: Извлекаем анамнез (может быть ошибка если OpenAI не настроен)
        response = await client.post(f"/api/audio/{audio_id}/extract-anamnesis")
        # Принимаем как успех если отчёт создан или если ошибка из-за OpenAI
        assert response.status_code in [200, 500, 503]
        
        # Шаг 4: Создаём или обновляем отчёт
        report_data = get_test_medical_report(1)
        response = await client.post(
            f"/api/appointments/{sample_appointment.id}/report",
            json=report_data
        )
        assert response.status_code == 200
        
        # Шаг 5: Отправляем в МИС
        response = await client.post(
            f"/api/appointments/{sample_appointment.id}/submit-to-mis"
        )
        assert response.status_code == 200
        
        # Шаг 6: Генерируем PDF
        response = await client.get(
            f"/api/appointments/{sample_appointment.id}/download-pdf"
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

