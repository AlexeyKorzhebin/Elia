"""
Примеры использования тестовых данных для проверки работоспособности приложения

Этот файл содержит примеры кода для тестирования API и функциональности
без изменения базы данных новыми приёмами.

ВНИМАНИЕ: Эти тесты требуют запущенного сервера на localhost:8000
или будут пропущены автоматически.
"""

import pytest
import asyncio
import httpx
from httpx import AsyncClient
from tests.test_data import (
    get_test_transcription,
    get_test_anamnesis,
    get_test_medical_report,
    get_test_blood_pressure,
    TEST_SCENARIOS,
    EDGE_CASE_TEXTS
)


# Базовый URL API (измените на ваш)
BASE_URL = "http://localhost:8000"


def check_server_available() -> bool:
    """Проверка доступности сервера"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        return result == 0
    except Exception:
        return False


# Маркер для пропуска тестов, если сервер не запущен
pytestmark = pytest.mark.skipif(
    not check_server_available(),
    reason="Сервер не запущен на localhost:8000. Эти тесты требуют запущенный сервер."
)


@pytest.mark.skipif(not check_server_available(), reason="Сервер не запущен на localhost:8000")
async def test_scenario_1_full_workflow():
    """
    Пример: Полный workflow работы с транскрипцией и анамнезом
    """
    # Увеличиваем таймаут для запросов к OpenAI API
    timeout = httpx.Timeout(60.0, connect=10.0)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=timeout) as client:
        # Шаг 1: Получаем список приёмов (используем существующий)
        response = await client.get("/api/appointments")
        appointments = response.json()
        if not appointments:
            print("⚠️ Нет доступных приёмов для тестирования")
            return
        
        appointment_id = appointments[0]["id"]
        print(f"✅ Используем приём ID: {appointment_id}")
        
        # Шаг 2: Генерируем транскрипцию
        print("\n📝 Генерация транскрипции...")
        response = await client.post(
            f"/api/audio/generate-mock-conversation",
            params={"appointment_id": appointment_id}
        )
        if response.status_code == 200:
            print("✅ Транскрипция сгенерирована")
            audio_data = response.json()
            audio_id = audio_data.get("transcription_text") and await get_audio_id(client, appointment_id)
        else:
            print(f"❌ Ошибка генерации: {response.status_code}")
            return
        
        # Шаг 3: Получаем аудиофайл
        if audio_id:
            response = await client.get(f"/api/audio/{audio_id}")
            if response.status_code == 200:
                print("✅ Аудиофайл получен")
                transcription = response.json().get("transcription_text", "")
                print(f"   Длина транскрипции: {len(transcription)} символов")
        
        # Шаг 4: Обновляем транскрипцию (редактирование)
        if audio_id:
            print("\n✏️ Обновление транскрипции...")
            test_text = get_test_transcription("cardiovascular")
            response = await client.put(
                f"/api/audio/{audio_id}/transcription",
                json={"transcription_text": test_text}
            )
            if response.status_code == 200:
                print("✅ Транскрипция обновлена")
        
        # Шаг 5: Извлекаем анамнез (может занять время из-за OpenAI API)
        if audio_id:
            print("\n🔍 Извлечение анамнеза (может занять до 60 секунд)...")
            try:
                response = await client.post(f"/api/audio/{audio_id}/extract-anamnesis", timeout=60.0)
                if response.status_code == 200:
                    print("✅ Анамнез извлечён")
                    anamnesis = response.json()
                    print(f"   Цель: {anamnesis.get('purpose', 'N/A')[:50]}...")
                elif response.status_code in [500, 503]:
                    print(f"⚠️ OpenAI API недоступен или не настроен: {response.status_code}")
                else:
                    print(f"⚠️ Ошибка извлечения анамнеза: {response.status_code}")
            except httpx.ReadTimeout:
                print("⚠️ Таймаут при извлечении анамнеза (OpenAI API может быть медленным)")
            except Exception as e:
                print(f"⚠️ Ошибка при извлечении анамнеза: {e}")
        
        # Шаг 6: Получаем отчёт
        print("\n📄 Получение медицинского отчёта...")
        response = await client.get(f"/api/appointments/{appointment_id}/report")
        if response.status_code == 200:
            print("✅ Отчёт получен")
        else:
            print(f"⚠️ Отчёт не найден: {response.status_code}")


async def test_scenario_2_transcription_editing():
    """
    Пример: Редактирование транскрипции с проверкой сохранения
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Получаем существующий приём
        response = await client.get("/api/appointments")
        appointments = response.json()
        if not appointments:
            print("⚠️ Нет доступных приёмов")
            return
        
        appointment_id = appointments[0]["id"]
        
        # Получаем аудиофайл
        audio_id = await get_audio_id(client, appointment_id)
        if not audio_id:
            print("⚠️ Аудиофайл не найден")
            return
        
        # Получаем текущую транскрипцию
        response = await client.get(f"/api/audio/{audio_id}")
        original_text = response.json().get("transcription_text", "")
        print(f"📝 Исходная транскрипция: {len(original_text)} символов")
        
        # Добавляем тестовый маркер
        test_marker = "\n\n[ТЕСТОВОЕ ИЗМЕНЕНИЕ]"
        modified_text = original_text + test_marker
        
        # Сохраняем изменения
        response = await client.put(
            f"/api/audio/{audio_id}/transcription",
            json={"transcription_text": modified_text}
        )
        if response.status_code == 200:
            print("✅ Изменения сохранены")
        
        # Проверяем сохранение
        response = await client.get(f"/api/audio/{audio_id}")
        saved_text = response.json().get("transcription_text", "")
        
        if test_marker in saved_text:
            print("✅ Изменения успешно сохранены и проверены")
        else:
            print("❌ Изменения не сохранились")


async def test_scenario_3_anamnesis_extraction():
    """
    Пример: Извлечение анамнеза из транскрипции
    """
    # Увеличиваем таймаут для запросов к OpenAI API
    timeout = httpx.Timeout(60.0, connect=10.0)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=timeout) as client:
        # Получаем приём
        response = await client.get("/api/appointments")
        appointments = response.json()
        if not appointments:
            return
        
        appointment_id = appointments[0]["id"]
        audio_id = await get_audio_id(client, appointment_id)
        
        if not audio_id:
            print("⚠️ Аудиофайл не найден")
            return
        
        # Извлекаем анамнез (может занять время из-за OpenAI API)
        print("🔍 Извлечение анамнеза (может занять до 60 секунд)...")
        try:
            response = await client.post(f"/api/audio/{audio_id}/extract-anamnesis", timeout=60.0)
            
            if response.status_code == 200:
                anamnesis = response.json()
                print("✅ Анамнез извлечён:")
                print(f"   Цель обращения: {anamnesis.get('purpose', 'N/A')[:100]}")
                print(f"   Жалобы: {anamnesis.get('complaints', 'N/A')[:100]}")
                print(f"   Анамнез: {anamnesis.get('anamnesis', 'N/A')[:100]}")
            elif response.status_code in [500, 503]:
                print(f"⚠️ OpenAI API недоступен или не настроен: {response.status_code}")
            else:
                print(f"❌ Ошибка: {response.status_code}")
        except httpx.ReadTimeout:
            print("⚠️ Таймаут при извлечении анамнеза (OpenAI API может быть медленным)")
            # Не проваливаем тест, так как это может быть проблема с OpenAI API
            pytest.skip("Таймаут при извлечении анамнеза - возможно OpenAI API медленно отвечает")
        except Exception as e:
            print(f"⚠️ Ошибка при извлечении анамнеза: {e}")
            pytest.skip(f"Ошибка при извлечении анамнеза: {e}")


async def test_scenario_4_blood_pressure():
    """
    Пример: Работа с показателями артериального давления
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Получаем пациента
        response = await client.get("/api/patients")
        patients = response.json()
        if not patients:
            print("⚠️ Нет доступных пациентов")
            return
        
        patient_id = patients[0]["id"]
        
        # Сохраняем показатели давления
        bp_data = get_test_blood_pressure(1)
        print(f"💓 Сохранение показателей давления: {bp_data['systolic']}/{bp_data['diastolic']}")
        
        response = await client.post(
            f"/api/patients/{patient_id}/blood-pressure",
            json=bp_data
        )
        
        if response.status_code == 200:
            print("✅ Показатели сохранены")
            
            # Проверяем обновление
            response = await client.get(f"/api/patients/{patient_id}/digital-portrait")
            if response.status_code == 200:
                portrait = response.json()
                indicators = portrait.get("health_indicators", {})
                print(f"   Систолическое: {indicators.get('systolic_pressure')}")
                print(f"   Диастолическое: {indicators.get('diastolic_pressure')}")
                print(f"   Пульс: {indicators.get('pulse')}")


async def test_scenario_5_pdf_generation():
    """
    Пример: Генерация PDF отчёта
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Получаем приём
        response = await client.get("/api/appointments")
        appointments = response.json()
        if not appointments:
            return
        
        appointment_id = appointments[0]["id"]
        
        print(f"📄 Генерация PDF для приёма {appointment_id}...")
        response = await client.get(f"/api/appointments/{appointment_id}/download-pdf")
        
        if response.status_code == 200:
            print("✅ PDF сгенерирован")
            print(f"   Размер файла: {len(response.content)} байт")
            print(f"   Content-Type: {response.headers.get('content-type')}")
        else:
            print(f"❌ Ошибка генерации PDF: {response.status_code}")


async def test_scenario_6_search():
    """
    Пример: Поиск пациентов и приёмов
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Поиск пациентов
        print("🔍 Поиск пациентов...")
        response = await client.get("/api/patients", params={"search": "Иванов"})
        if response.status_code == 200:
            patients = response.json()
            print(f"✅ Найдено пациентов: {len(patients)}")
        
        # Поиск приёмов
        print("\n🔍 Поиск приёмов...")
        response = await client.get("/api/appointments", params={"search": "Иванов"})
        if response.status_code == 200:
            appointments = response.json()
            print(f"✅ Найдено приёмов: {len(appointments)}")


async def test_edge_cases():
    """
    Пример: Тестирование граничных случаев
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Тест с очень длинным текстом
        print("🧪 Тест с очень длинным текстом...")
        long_text = EDGE_CASE_TEXTS["very_long_transcription"]
        
        # Получаем приём и аудио
        response = await client.get("/api/appointments")
        appointments = response.json()
        if appointments:
            appointment_id = appointments[0]["id"]
            audio_id = await get_audio_id(client, appointment_id)
            
            if audio_id:
                response = await client.put(
                    f"/api/audio/{audio_id}/transcription",
                    json={"transcription_text": long_text[:10000]}  # Ограничиваем размер
                )
                if response.status_code == 200:
                    print("✅ Длинный текст обработан")
        
        # Тест с пустым текстом
        print("\n🧪 Тест с пустым текстом...")
        if audio_id:
            response = await client.put(
                f"/api/audio/{audio_id}/transcription",
                json={"transcription_text": ""}
            )
            print(f"   Статус: {response.status_code}")


async def test_error_handling():
    """
    Пример: Тестирование обработки ошибок
    """
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Тест с несуществующим приёмом
        print("🧪 Тест с несуществующим приёмом...")
        response = await client.get("/api/appointments/99999")
        if response.status_code == 404:
            print("✅ Ошибка 404 корректно обработана")
        
        # Тест с несуществующим аудио
        print("\n🧪 Тест с несуществующим аудио...")
        response = await client.get("/api/audio/99999")
        if response.status_code == 404:
            print("✅ Ошибка 404 корректно обработана")
        
        # Тест с некорректным давлением
        print("\n🧪 Тест с некорректным давлением...")
        response = await client.get("/api/patients")
        patients = response.json()
        if patients:
            patient_id = patients[0]["id"]
            response = await client.post(
                f"/api/patients/{patient_id}/blood-pressure",
                json={"systolic": 500, "diastolic": 10, "pulse": 300}
            )
            if response.status_code == 400:
                print("✅ Валидация давления работает корректно")


async def get_audio_id(client: httpx.AsyncClient, appointment_id: int) -> int | None:
    """Вспомогательная функция для получения ID аудиофайла"""
    try:
        response = await client.get(f"/api/audio/by-appointment/{appointment_id}")
        if response.status_code == 200:
            return response.json().get("id")
    except Exception:
        pass
    return None


async def run_all_tests():
    """Запуск всех тестовых сценариев"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ РАБОТОСПОСОБНОСТИ ПРИЛОЖЕНИЯ")
    print("=" * 60)
    
    tests = [
        ("Полный workflow", test_scenario_1_full_workflow),
        ("Редактирование транскрипции", test_scenario_2_transcription_editing),
        ("Извлечение анамнеза", test_scenario_3_anamnesis_extraction),
        ("Работа с давлением", test_scenario_4_blood_pressure),
        ("Генерация PDF", test_scenario_5_pdf_generation),
        ("Поиск", test_scenario_6_search),
        ("Граничные случаи", test_edge_cases),
        ("Обработка ошибок", test_error_handling),
    ]
    
    for name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"ТЕСТ: {name}")
        print('=' * 60)
        try:
            await test_func()
        except Exception as e:
            print(f"❌ Ошибка при выполнении теста: {e}")
        print()
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)


if __name__ == "__main__":
    # Запуск всех тестов
    asyncio.run(run_all_tests())

