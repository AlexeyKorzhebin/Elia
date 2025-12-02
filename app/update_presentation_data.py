"""Скрипт для обновления тестовых данных для презентации"""
import asyncio
from datetime import date
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import async_session_maker, init_db
from app.models import (
    Patient, ChronicDisease, RecentDisease, HealthIndicator,
    Appointment, MedicalReport, AudioFile,
    GenderEnum, AppointmentStatus
)


async def update_presentation_data():
    """Обновить тестовые данные для презентации"""
    
    # Инициализируем БД
    await init_db()
    
    async with async_session_maker() as session:
        # Удаляем все старые данные
        print("🗑️  Удаление старых данных...")
        
        # Удаляем в правильном порядке из-за внешних ключей
        await session.execute(delete(MedicalReport))
        await session.execute(delete(AudioFile))
        await session.execute(delete(Appointment))
        await session.execute(delete(HealthIndicator))
        await session.execute(delete(ChronicDisease))
        await session.execute(delete(RecentDisease))
        await session.execute(delete(Patient))
        
        await session.commit()
        print("✅ Старые данные удалены")
        
        # Создаём новых пациентов
        print("👥 Создание новых пациентов...")
        
        patients_data = [
            {
                "first_name": "Мария",
                "last_name": "Величко",
                "middle_name": "Александровна",
                # Возраст 17 лет на 1.12.2025
                # Дата рождения: 5.12.2007 (чтобы на 1.12.2025 было 17 лет, день рождения еще не прошел)
                "date_of_birth": date(2007, 12, 5),
                "gender": GenderEnum.FEMALE,
                "medical_organization": "ГБУЗ Поликлиника №7",
                "medical_area": "Терапевтический 7",
                "last_visit_date": date(2025, 11, 20),
                "chronic": ["Гипертония"],
                "recent": ["ОРВИ"],
                "health": {"hemoglobin": 12.8, "cholesterol": 5.1, "bmi": 23.5, "heart_rate": 72}
            },
            {
                "first_name": "Михаил",
                "last_name": "Боков",
                "middle_name": "Николаевич",
                # Возраст 17 лет на 1.12.2025
                # Дата рождения: 3.12.2007 (чтобы на 1.12.2025 было 17 лет, день рождения еще не прошел)
                "date_of_birth": date(2007, 12, 3),
                "gender": GenderEnum.MALE,
                "medical_organization": "ГБУЗ Поликлиника №3",
                "medical_area": "Терапевтический 3",
                "last_visit_date": date(2025, 11, 15),
                "chronic": ["Сахарный диабет 2 типа"],
                "recent": [],
                "health": {"hemoglobin": 14.2, "cholesterol": 5.8, "bmi": 26.3, "heart_rate": 78}
            },
            {
                "first_name": "Тимофей",
                "last_name": "Арзамасцев",
                "middle_name": "Дмитриевич",
                # Возраст 18 лет на 1.12.2025
                # Дата рождения: 7.12.2006 (чтобы на 1.12.2025 было 18 лет, день рождения еще не прошел)
                "date_of_birth": date(2006, 12, 7),
                "gender": GenderEnum.MALE,
                "medical_organization": "ГБУЗ Поликлиника №5",
                "medical_area": "Терапевтический 5",
                "last_visit_date": date(2025, 11, 25),
                "chronic": [],
                "recent": ["Бронхит"],
                "health": {"hemoglobin": 15.1, "cholesterol": 4.5, "bmi": 24.8, "heart_rate": 68}
            },
            {
                "first_name": "Анастасия",
                "last_name": "Коржебина",
                "middle_name": "Алексеевна",
                # Возраст 17 лет на 1.12.2025
                # Дата рождения: 7.12.2007 (чтобы на 1.12.2025 было 17 лет, день рождения еще не прошел)
                "date_of_birth": date(2007, 12, 7),
                "gender": GenderEnum.FEMALE,
                "medical_organization": "ГБУЗ Поликлиника №2",
                "medical_area": "Терапевтический 2",
                "last_visit_date": date(2025, 11, 28),
                "chronic": ["Анемия"],
                "recent": ["Головная боль"],
                "health": {"hemoglobin": 11.5, "cholesterol": 4.9, "bmi": 22.1, "heart_rate": 74}
            }
        ]
        
        patients = []
        for data in patients_data:
            patient = Patient(
                first_name=data["first_name"],
                last_name=data["last_name"],
                middle_name=data["middle_name"],
                date_of_birth=data["date_of_birth"],
                gender=data["gender"],
                medical_organization=data["medical_organization"],
                medical_area=data["medical_area"],
                last_visit_date=data["last_visit_date"]
            )
            session.add(patient)
            await session.flush()
            
            # Добавляем хронические заболевания
            for disease_name in data["chronic"]:
                chronic = ChronicDisease(patient_id=patient.id, name=disease_name)
                session.add(chronic)
            
            # Добавляем последние заболевания
            for disease_name in data["recent"]:
                recent = RecentDisease(patient_id=patient.id, name=disease_name)
                session.add(recent)
            
            # Добавляем показатели здоровья
            if data["health"]:
                indicator = HealthIndicator(
                    patient_id=patient.id,
                    hemoglobin=data["health"].get("hemoglobin"),
                    cholesterol=data["health"].get("cholesterol"),
                    bmi=data["health"].get("bmi"),
                    heart_rate=data["health"].get("heart_rate")
                )
                session.add(indicator)
            
            patients.append(patient)
        
        await session.commit()
        print(f"✅ Создано {len(patients)} пациентов")
        
        # Создаём приёмы
        print("📅 Создание приёмов...")
        
        appointments_data = [
            # Величко Мария Александровна, 5.12.25 16:37
            (0, date(2025, 12, 5), "16:37", "16:55", AppointmentStatus.ANALYSIS, False),
            # Боков Михаил Николаевич, 3.12.25 11:33
            (1, date(2025, 12, 3), "11:33", "11:50", AppointmentStatus.REFERRAL, False),
            # Арзамасцев Тимофей Дмитриевич, 7.12.25 14:23 (последний - будет подсвечен)
            (2, date(2025, 12, 7), "14:23", "14:40", AppointmentStatus.COLD, False),
            # Коржебина Анастасия Алексеевна, 7.12.25 13:34
            (3, date(2025, 12, 7), "13:34", "13:50", AppointmentStatus.ANEMIA, False),
        ]
        
        for patient_idx, app_date, time_start, time_end, status, is_active in appointments_data:
            appointment = Appointment(
                patient_id=patients[patient_idx].id,
                appointment_date=app_date,
                appointment_time_start=time_start,
                appointment_time_end=time_end,
                status=status,
                is_active=is_active
            )
            session.add(appointment)
        
        await session.commit()
        print(f"✅ Создано {len(appointments_data)} приёмов")
        
        # Выводим итоговую информацию
        print("\n📊 Итоговая информация:")
        result = await session.execute(select(Patient))
        all_patients = result.scalars().all()
        for patient in all_patients:
            print(f"  - {patient.full_name} ({patient.gender.value})")
        
        result = await session.execute(select(Appointment).options(selectinload(Appointment.patient)))
        all_appointments = result.scalars().all()
        for appointment in all_appointments:
            print(f"  - {appointment.patient.full_name}: {appointment.appointment_date} {appointment.appointment_time_start} ({appointment.status.value})")
        
        print("\n✅ Тестовые данные для презентации успешно обновлены!")


if __name__ == "__main__":
    asyncio.run(update_presentation_data())

