#!/usr/bin/env python3
"""
Быстрый скрипт для проверки работоспособности приложения
Использует существующие данные из БД, не создаёт новые приёмы
"""

import asyncio
import sys
import httpx
from tests.test_data import (
    get_test_transcription,
    get_test_anamnesis,
    get_test_medical_report
)


BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


async def check_health():
    """Проверка health check endpoint"""
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=5.0) as client:
            response = await client.get("/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Сервер работает: {data.get('app')} v{data.get('version')}")
                return True
            else:
                print(f"❌ Health check вернул статус {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Не удалось подключиться к серверу: {e}")
        print(f"   Убедитесь, что сервер запущен на {BASE_URL}")
        return False


async def check_appointments():
    """Проверка наличия приёмов"""
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get("/api/appointments")
            if response.status_code == 200:
                appointments = response.json()
                if appointments:
                    print(f"✅ Найдено приёмов: {len(appointments)}")
                    return appointments[0]["id"]
                else:
                    print("⚠️ Приёмов не найдено")
                    return None
            else:
                print(f"❌ Ошибка получения приёмов: {response.status_code}")
                return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


async def check_patients():
    """Проверка наличия пациентов"""
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get("/api/patients")
            if response.status_code == 200:
                patients = response.json()
                if patients:
                    print(f"✅ Найдено пациентов: {len(patients)}")
                    return patients[0]["id"]
                else:
                    print("⚠️ Пациентов не найдено")
                    return None
            else:
                print(f"❌ Ошибка получения пациентов: {response.status_code}")
                return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


async def test_transcription_update(appointment_id: int):
    """Тест обновления транскрипции"""
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            # Получаем аудиофайл
            response = await client.get(f"/api/audio/by-appointment/{appointment_id}")
            if response.status_code != 200:
                print(f"⚠️ Аудиофайл не найден для приёма {appointment_id}")
                return False
            
            audio_id = response.json()["id"]
            transcription = get_test_transcription("short")
            
            # Обновляем транскрипцию
            response = await client.put(
                f"/api/audio/{audio_id}/transcription",
                json={"transcription_text": transcription}
            )
            
            if response.status_code == 200:
                print("✅ Транскрипция успешно обновлена")
                return True
            else:
                print(f"❌ Ошибка обновления транскрипции: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def test_anamnesis_extraction(appointment_id: int):
    """Тест извлечения анамнеза"""
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            # Получаем аудиофайл
            response = await client.get(f"/api/audio/by-appointment/{appointment_id}")
            if response.status_code != 200:
                print(f"⚠️ Аудиофайл не найден для приёма {appointment_id}")
                return False
            
            audio_id = response.json()["id"]
            
            # Проверяем наличие транскрипции
            response = await client.get(f"/api/audio/{audio_id}")
            if not response.json().get("transcription_text"):
                print("⚠️ Транскрипция отсутствует, пропускаем тест")
                return False
            
            # Извлекаем анамнез
            print("   Извлечение анамнеза (может занять время)...")
            response = await client.post(f"/api/audio/{audio_id}/extract-anamnesis")
            
            if response.status_code == 200:
                anamnesis = response.json()
                print("✅ Анамнез успешно извлечён")
                if anamnesis.get("purpose"):
                    print(f"   Цель: {anamnesis['purpose'][:60]}...")
                return True
            else:
                print(f"❌ Ошибка извлечения анамнеза: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def test_medical_report(appointment_id: int):
    """Тест создания/обновления медицинского отчёта"""
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            report_data = get_test_medical_report(1)
            
            response = await client.post(
                f"/api/appointments/{appointment_id}/report",
                json=report_data
            )
            
            if response.status_code == 200:
                print("✅ Медицинский отчёт успешно сохранён")
                return True
            else:
                print(f"❌ Ошибка сохранения отчёта: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def test_pdf_generation(appointment_id: int):
    """Тест генерации PDF"""
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get(f"/api/appointments/{appointment_id}/download-pdf")
            
            if response.status_code == 200:
                pdf_size = len(response.content)
                print(f"✅ PDF успешно сгенерирован ({pdf_size} байт)")
                return True
            else:
                print(f"⚠️ Ошибка генерации PDF: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def run_quick_tests():
    """Запуск быстрых тестов"""
    print("=" * 60)
    print("БЫСТРАЯ ПРОВЕРКА РАБОТОСПОСОБНОСТИ ПРИЛОЖЕНИЯ")
    print("=" * 60)
    print()
    
    # Проверка health check
    print("1. Проверка сервера...")
    if not await check_health():
        print("\n❌ Сервер недоступен. Запустите сервер и попробуйте снова.")
        sys.exit(1)
    print()
    
    # Проверка приёмов
    print("2. Проверка наличия приёмов...")
    appointment_id = await check_appointments()
    if not appointment_id:
        print("\n⚠️ Нет доступных приёмов для тестирования")
        sys.exit(0)
    print()
    
    # Проверка пациентов
    print("3. Проверка наличия пациентов...")
    patient_id = await check_patients()
    print()
    
    # Тесты
    results = []
    
    print("4. Тест обновления транскрипции...")
    results.append(await test_transcription_update(appointment_id))
    print()
    
    print("5. Тест извлечения анамнеза...")
    results.append(await test_anamnesis_extraction(appointment_id))
    print()
    
    print("6. Тест сохранения медицинского отчёта...")
    results.append(await test_medical_report(appointment_id))
    print()
    
    print("7. Тест генерации PDF...")
    results.append(await test_pdf_generation(appointment_id))
    print()
    
    # Итоги
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"РЕЗУЛЬТАТЫ: {passed}/{total} тестов пройдено")
    print("=" * 60)
    
    if passed == total:
        print("✅ Все тесты пройдены успешно!")
        sys.exit(0)
    else:
        print("⚠️ Некоторые тесты не пройдены")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(run_quick_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️ Тестирование прервано пользователем")
        sys.exit(1)

