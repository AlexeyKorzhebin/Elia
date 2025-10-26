"""Тестовые данные для демонстрации системы"""
import asyncio
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker, init_db
from app.models import (
    Patient, ChronicDisease, RecentDisease, HealthIndicator,
    Appointment, GenderEnum, AppointmentStatus
)


async def load_fixtures():
    """Загрузить тестовые данные в БД"""
    
    # Инициализируем БД
    await init_db()
    
    async with async_session_maker() as session:
        # Проверяем, есть ли уже данные
        from sqlalchemy import select
        result = await session.execute(select(Patient))
        if result.first():
            print("Фикстуры уже загружены")
            return
        
        # Создаём пациентов
        patients_data = [
            {
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Алексеевич",
                "date_of_birth": date(1985, 3, 15),
                "gender": GenderEnum.MALE,
                "medical_organization": "ГБУЗ Поликлиника №7",
                "medical_area": "Терапевтический 7",
                "last_visit_date": date(2025, 7, 20),
                "chronic": ["Сахарный диабет", "Анемия", "Астма"],
                "recent": ["Инфекционный мононуклеоз", "Пневмания"],
                "health": {"hemoglobin": 13.8, "cholesterol": 4.8, "bmi": 24.2, "heart_rate": 74}
            },
            {
                "first_name": "Милена",
                "last_name": "Петрова",
                "middle_name": "Игоревна",
                "date_of_birth": date(1992, 7, 22),
                "gender": GenderEnum.FEMALE,
                "medical_organization": "ГБУЗ Поликлиника №3",
                "medical_area": "Терапевтический 3",
                "last_visit_date": date(2025, 8, 15),
                "chronic": ["Гипертония"],
                "recent": ["ОРВИ"],
                "health": {"hemoglobin": 12.5, "cholesterol": 5.2, "bmi": 22.1, "heart_rate": 68}
            },
            {
                "first_name": "Александр",
                "last_name": "Эцкерев",
                "middle_name": "Владимирович",
                "date_of_birth": date(1978, 11, 8),
                "gender": GenderEnum.MALE,
                "medical_organization": "ГБУЗ Поликлиника №5",
                "medical_area": "Терапевтический 12",
                "last_visit_date": date(2025, 9, 1),
                "chronic": ["ОРВИ"],
                "recent": [],
                "health": {"hemoglobin": 14.2, "cholesterol": 4.5, "bmi": 26.8, "heart_rate": 72}
            },
            {
                "first_name": "Илья",
                "last_name": "Малинин",
                "middle_name": "Авдотьевич",
                "date_of_birth": date(1995, 4, 12),
                "gender": GenderEnum.MALE,
                "medical_organization": "ГБУЗ Поликлиника №7",
                "medical_area": "Терапевтический 5",
                "last_visit_date": date(2025, 10, 10),
                "chronic": [],
                "recent": [],
                "health": {"hemoglobin": 15.1, "cholesterol": 4.0, "bmi": 23.5, "heart_rate": 70}
            },
            {
                "first_name": "Мирон",
                "last_name": "Сизов",
                "middle_name": "Генадьевич",
                "date_of_birth": date(1988, 6, 30),
                "gender": GenderEnum.MALE,
                "medical_organization": "ГБУЗ Поликлиника №2",
                "medical_area": "Терапевтический 8",
                "last_visit_date": date(2025, 6, 5),
                "chronic": ["Аллергический ринит"],
                "recent": ["Анемия"],
                "health": {"hemoglobin": 13.0, "cholesterol": 5.5, "bmi": 28.3, "heart_rate": 78}
            },
            {
                "first_name": "Игнат",
                "last_name": "Ехимов",
                "middle_name": "Михайлович",
                "date_of_birth": date(1982, 9, 17),
                "gender": GenderEnum.MALE,
                "medical_organization": "ГБУЗ Поликлиника №1",
                "medical_area": "Терапевтический 4",
                "last_visit_date": date(2025, 5, 22),
                "chronic": ["Головная боль"],
                "recent": [],
                "health": {"hemoglobin": 14.5, "cholesterol": 4.2, "bmi": 25.0, "heart_rate": 69}
            },
            {
                "first_name": "Пётр",
                "last_name": "Гуменников",
                "middle_name": "Петрович",
                "date_of_birth": date(1990, 12, 5),
                "gender": GenderEnum.MALE,
                "medical_organization": "ГБУЗ Поликлиника №4",
                "medical_area": "Терапевтический 9",
                "last_visit_date": date(2025, 4, 18),
                "chronic": ["ОРВИ"],
                "recent": [],
                "health": {"hemoglobin": 13.5, "cholesterol": 4.7, "bmi": 24.8, "heart_rate": 73}
            },
            {
                "first_name": "Людмила",
                "last_name": "Терентьева",
                "middle_name": "Ивановна",
                "date_of_birth": date(1987, 2, 25),
                "gender": GenderEnum.FEMALE,
                "medical_organization": "ГБУЗ Поликлиника №6",
                "medical_area": "Терапевтический 11",
                "last_visit_date": date(2025, 3, 30),
                "chronic": ["Инфекционный мононуклеоз"],
                "recent": [],
                "health": {"hemoglobin": 12.8, "cholesterol": 5.0, "bmi": 21.5, "heart_rate": 66}
            },
            {
                "first_name": "Анна",
                "last_name": "Смирнова",
                "middle_name": "Петровна",
                "date_of_birth": date(1993, 5, 10),
                "gender": GenderEnum.FEMALE,
                "medical_organization": "ГБУЗ Поликлиника №3",
                "medical_area": "Терапевтический 6",
                "last_visit_date": date(2025, 2, 14),
                "chronic": ["Остеохондроз"],
                "recent": ["Бронхит"],
                "health": {"hemoglobin": 13.2, "cholesterol": 4.6, "bmi": 20.9, "heart_rate": 71}
            },
            {
                "first_name": "Дмитрий",
                "last_name": "Кузнецов",
                "middle_name": "Сергеевич",
                "date_of_birth": date(1980, 8, 20),
                "gender": GenderEnum.MALE,
                "medical_organization": "ГБУЗ Поликлиника №5",
                "medical_area": "Терапевтический 10",
                "last_visit_date": date(2025, 1, 8),
                "chronic": ["Язва желудка"],
                "recent": [],
                "health": {"hemoglobin": 14.0, "cholesterol": 5.3, "bmi": 27.2, "heart_rate": 75}
            },
            {
                "first_name": "Елена",
                "last_name": "Волкова",
                "middle_name": "Андреевна",
                "date_of_birth": date(1991, 10, 3),
                "gender": GenderEnum.FEMALE,
                "medical_organization": "ГБУЗ Поликлиника №2",
                "medical_area": "Терапевтический 2",
                "last_visit_date": date(2024, 12, 20),
                "chronic": [],
                "recent": ["Ангина"],
                "health": {"hemoglobin": 12.3, "cholesterol": 4.3, "bmi": 22.7, "heart_rate": 67}
            },
            {
                "first_name": "Сергей",
                "last_name": "Морозов",
                "middle_name": "Викторович",
                "date_of_birth": date(1986, 1, 28),
                "gender": GenderEnum.MALE,
                "medical_organization": "ГБУЗ Поликлиника №8",
                "medical_area": "Терапевтический 1",
                "last_visit_date": date(2024, 11, 15),
                "chronic": ["Гастрит"],
                "recent": [],
                "health": {"hemoglobin": 14.8, "cholesterol": 4.9, "bmi": 25.5, "heart_rate": 72}
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
        
        # Создаём приёмы
        today = date.today()
        appointments_data = [
            # Четверг, 16 октября
            (0, today - timedelta(days=10), "16:10", "16:20", AppointmentStatus.SCHEDULED, True),
            (1, today - timedelta(days=10), "15:45", "16:00", AppointmentStatus.ANEMIA, False),
            (2, today - timedelta(days=10), "15:20", "15:40", AppointmentStatus.HEADACHE, False),
            (3, today - timedelta(days=10), "11:40", "12:00", AppointmentStatus.REFERRAL, False),
            
            # Среда, 15 октября
            (4, today - timedelta(days=11), "12:00", "12:20", AppointmentStatus.ANEMIA, False),
            (5, today - timedelta(days=11), "11:45", "12:05", AppointmentStatus.HEADACHE, False),
            (6, today - timedelta(days=11), "11:10", "11:30", AppointmentStatus.COLD, False),
            (7, today - timedelta(days=11), "10:50", "11:10", AppointmentStatus.MONONUCLEOSIS, False),
            
            # Дополнительные приёмы
            (8, today - timedelta(days=12), "14:00", "14:20", AppointmentStatus.ANALYSIS, False),
            (9, today - timedelta(days=13), "10:30", "10:50", AppointmentStatus.COLD, False),
            (10, today - timedelta(days=14), "16:00", "16:20", AppointmentStatus.SCHEDULED, False),
            (11, today - timedelta(days=15), "13:30", "13:50", AppointmentStatus.HEADACHE, False),
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
        
        print(f"✅ Загружено {len(patients)} пациентов и {len(appointments_data)} приёмов")


if __name__ == "__main__":
    asyncio.run(load_fixtures())

