"""API endpoints для работы с аудиофайлами"""
import asyncio
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud
from app.config import settings
from app.models import TranscriptionStatus
from app.schemas import (
    AudioFileSchema,
    AudioUploadResponse,
    TranscriptionResponse,
    MedicalReportSchema
)
from app.openai_service import openai_service
from app.logger import get_logger

router = APIRouter(prefix="/api/audio", tags=["audio"])
logger = get_logger(__name__)

# Допустимые типы аудиофайлов
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/wave"}
ALLOWED_EXTENSIONS = {".mp3", ".wav"}


def get_upload_dir() -> Path:
    """Получить путь к директории для загрузок"""
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


@router.post("/upload", response_model=AudioUploadResponse)
async def upload_audio_file(
    appointment_id: int = Query(..., description="ID приёма"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Загрузить аудиофайл для приёма"""
    
    # Проверяем, существует ли приём
    appointment = await crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Приём не найден")
    
    # Проверяем, не загружен ли уже аудиофайл
    existing_audio = await crud.get_audio_file_by_appointment(db, appointment_id)
    if existing_audio:
        raise HTTPException(status_code=400, detail="Аудиофайл уже загружен для этого приёма")
    
    # Проверяем тип файла
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла. Допустимые форматы: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Генерируем уникальное имя файла
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    upload_dir = get_upload_dir()
    file_path = upload_dir / unique_filename
    
    # Сохраняем файл
    file_size = 0
    try:
        with open(file_path, "wb") as f:
            while chunk := await file.read(8192):
                file_size += len(chunk)
                if file_size > settings.max_upload_size:
                    # Удаляем частично загруженный файл
                    f.close()
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"Файл слишком большой. Максимальный размер: {settings.max_upload_size / 1024 / 1024:.0f}MB"
                    )
                f.write(chunk)
    except Exception as e:
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")
    
    # Создаём запись в БД
    audio = await crud.create_audio_file(
        db,
        appointment_id=appointment_id,
        filename=file.filename,
        filepath=str(file_path),
        file_size=file_size,
        mime_type=file.content_type or "audio/mpeg"
    )
    
    return AudioUploadResponse(
        id=audio.id,
        filename=audio.filename,
        file_size=audio.file_size,
        message="Аудиофайл успешно загружен"
    )


@router.put("/{audio_id}/transcription")
async def update_transcription_text(
    audio_id: int,
    transcription_text: str = Query(..., description="Обновлённый текст транскрипции"),
    db: AsyncSession = Depends(get_db)
):
    """Обновить текст транскрипции"""
    logger.info(f"Запрос на обновление транскрипции: audio_id={audio_id}")
    
    audio = await crud.get_audio_file(db, audio_id)
    if not audio:
        raise HTTPException(status_code=404, detail="Аудиофайл не найден")
    
    # Обновляем текст транскрипции
    audio = await crud.update_transcription(
        db,
        audio_id,
        TranscriptionStatus.COMPLETED,
        text=transcription_text
    )
    
    logger.info(f"Транскрипция обновлена: audio_id={audio_id}, text_length={len(transcription_text)}")
    
    return TranscriptionResponse(
        success=True,
        message="Транскрипция успешно обновлена",
        transcription_status=audio.transcription_status,
        transcription_text=audio.transcription_text,
        transcribed_at=audio.transcribed_at
    )


@router.post("/{audio_id}/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Имитация транскрибации аудиофайла"""
    
    # Получаем аудиофайл
    audio = await crud.get_audio_file(db, audio_id)
    if not audio:
        raise HTTPException(status_code=404, detail="Аудиофайл не найден")
    
    # Проверяем статус
    if audio.transcription_status == TranscriptionStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Аудиофайл уже транскрибирован")
    
    if audio.transcription_status == TranscriptionStatus.PROCESSING:
        raise HTTPException(status_code=400, detail="Транскрибация уже выполняется")
    
    # Устанавливаем статус "обработка"
    await crud.update_transcription(db, audio_id, TranscriptionStatus.PROCESSING)
    
    # Имитация обработки (5-7 секунд)
    await asyncio.sleep(6)
    
    # Фиктивная транскрипция
    fake_transcription = """
    Врач: Здравствуйте! Проходите, присаживайтесь. Что вас беспокоит?
    
    Пациент: Добрый день, доктор. Последние несколько дней у меня сильные боли в верхней части живота, особенно усиливаются после приема пищи. Также ощущаю тяжесть и жжение.
    
    Врач: Понятно. А когда именно начались эти симптомы? И с чем вы связываете их появление?
    
    Пациент: Примерно неделю назад. Может быть связано с тем, что в последнее время часто питаюсь нерегулярно, употребляю много кофе и часто перекусываю на работе острой пищей.
    
    Врач: Хорошо. Отмечали ли вы изжогу, отрыжку, тошноту? Были ли эпизоды рвоты?
    
    Пациент: Да, изжога беспокоит, особенно по утрам и после еды. Отрыжка тоже периодически бывает. Тошноты нет, рвоты не было.
    
    Врач: Принимали ли вы какие-либо препараты для облегчения симптомов?
    
    Пациент: Пробовал принимать антациды, немного помогают, но ненадолго.
    
    Врач: Ясно. Сейчас я вас осмотрю. Прилягте, пожалуйста, на кушетку. При пальпации отмечается болезненность в эпигастральной области. Напряжения мышц передней брюшной стенки нет. Печень, селезёнка не увеличены.
    
    Пациент: Ох, да, здесь как раз болит.
    
    Врач: На основании жалоб и осмотра у вас, вероятно, обострение гастрита или начинающаяся язвенная болезнь желудка. Я назначу вам обследование: общий анализ крови, анализ на Helicobacter pylori, а также гастроскопию для уточнения диагноза.
    
    Пациент: Хорошо, доктор.
    
    Врач: Также рекомендую придерживаться диеты: исключить острое, жирное, копчёное, кофе, алкоголь. Питаться часто, но небольшими порциями. Назначу вам препараты для снижения кислотности и защиты слизистой желудка.
    
    Пациент: Спасибо большое! Буду следовать рекомендациям.
    
    Врач: Результаты анализов принесёте на повторный приём через неделю. Если состояние ухудшится — сразу обращайтесь. Будьте здоровы!
    
    Пациент: Спасибо, до свидания!
    """
    
    # Обновляем статус на "завершено" с текстом транскрипции
    audio = await crud.update_transcription(
        db,
        audio_id,
        TranscriptionStatus.COMPLETED,
        text=fake_transcription.strip()
    )
    
    return TranscriptionResponse(
        success=True,
        message="Транскрибация завершена (MVP)",
        transcription_status=audio.transcription_status,
        transcription_text=audio.transcription_text,
        transcribed_at=audio.transcribed_at
    )


@router.get("/by-appointment/{appointment_id}", response_model=AudioFileSchema)
async def get_audio_by_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить аудиофайл по ID приёма"""
    audio = await crud.get_audio_file_by_appointment(db, appointment_id)
    if not audio:
        raise HTTPException(status_code=404, detail="Аудиофайл не найден для этого приёма")
    return audio


@router.get("/{audio_id}", response_model=AudioFileSchema)
async def get_audio_info(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить информацию об аудиофайле"""
    audio = await crud.get_audio_file(db, audio_id)
    if not audio:
        raise HTTPException(status_code=404, detail="Аудиофайл не найден")
    return audio


@router.get("/{audio_id}/download")
async def download_audio(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Скачать или проиграть аудиофайл"""
    audio = await crud.get_audio_file(db, audio_id)
    if not audio:
        raise HTTPException(status_code=404, detail="Аудиофайл не найден")
    
    file_path = Path(audio.filepath)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден на сервере")
    
    return FileResponse(
        path=file_path,
        media_type=audio.mime_type,
        filename=audio.filename
    )


@router.post("/generate-mock-conversation")
async def generate_mock_conversation(
    appointment_id: int = Query(..., description="ID приёма"),
    db: AsyncSession = Depends(get_db)
):
    """Сгенерировать mock-разговор через OpenAI API"""
    logger.info(f"Запрос генерации mock-разговора для приёма: appointment_id={appointment_id}")
    
    try:
        # Проверяем, существует ли приём
        appointment = await crud.get_appointment(db, appointment_id)
        if not appointment:
            logger.warning(f"Попытка генерации для несуществующего приёма: appointment_id={appointment_id}")
            raise HTTPException(status_code=404, detail="Приём не найден")
        
        # Получаем данные пациента
        patient = await crud.get_patient(db, appointment.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Пациент не найден")
        
        # Проверяем, не создан ли уже аудиофайл с транскрипцией
        existing_audio = await crud.get_audio_file_by_appointment(db, appointment_id)
        if existing_audio and existing_audio.transcription_text:
            logger.info(f"Для приёма {appointment_id} уже есть транскрипция, перегенерируем")
        
        # Генерируем диалог через OpenAI
        logger.debug(f"Генерация диалога для пациента: {patient.full_name}, возраст: {patient.age}")
        conversation = await openai_service.generate_conversation(
            patient_name=patient.full_name,
            patient_age=patient.age,
            patient_gender=patient.gender.value if hasattr(patient.gender, 'value') else str(patient.gender)
        )
        
        # Если аудиофайла нет, создаём запись
        if not existing_audio:
            # Создаём "виртуальный" аудиофайл (без реального файла)
            audio = await crud.create_audio_file(
                db,
                appointment_id=appointment_id,
                filename="generated_conversation.txt",
                filepath="",  # Нет реального файла
                file_size=len(conversation.encode('utf-8')),
                mime_type="text/plain"
            )
        else:
            audio = existing_audio
        
        # Обновляем транскрипцию
        audio = await crud.update_transcription(
            db,
            audio.id,
            TranscriptionStatus.COMPLETED,
            text=conversation
        )
        
        logger.info(f"Mock-разговор успешно сгенерирован и сохранён: appointment_id={appointment_id}, audio_id={audio.id}, text_length={len(conversation)}")
        
        return TranscriptionResponse(
            success=True,
            message="Разговор успешно сгенерирован через OpenAI",
            transcription_status=audio.transcription_status,
            transcription_text=audio.transcription_text,
            transcribed_at=audio.transcribed_at
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Ошибка конфигурации при генерации разговора: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при генерации mock-разговора: appointment_id={appointment_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации разговора: {str(e)}")


@router.post("/{audio_id}/extract-anamnesis", response_model=MedicalReportSchema)
async def extract_anamnesis_from_transcription(
    audio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Извлечь данные анамнеза из транскрипции через OpenAI API"""
    logger.info(f"Запрос извлечения анамнеза из транскрипции: audio_id={audio_id}")
    
    try:
        # Получаем аудиофайл
        audio = await crud.get_audio_file(db, audio_id)
        if not audio:
            logger.warning(f"Попытка извлечения анамнеза из несуществующего аудио: audio_id={audio_id}")
            raise HTTPException(status_code=404, detail="Аудиофайл не найден")
        
        # Проверяем наличие транскрипции
        if not audio.transcription_text:
            logger.warning(f"Попытка извлечения анамнеза без транскрипции: audio_id={audio_id}")
            raise HTTPException(status_code=400, detail="Транскрипция отсутствует. Сначала создайте транскрипцию.")
        
        # Извлекаем данные через OpenAI
        logger.debug(f"Извлечение данных анамнеза, длина транскрипции: {len(audio.transcription_text)}")
        anamnesis_data = await openai_service.extract_anamnesis_data(audio.transcription_text)
        
        # Получаем appointment_id
        appointment_id = audio.appointment_id
        
        # Создаём или обновляем медицинский отчёт
        report = await crud.create_or_update_medical_report(
            db,
            appointment_id,
            purpose=anamnesis_data.get("purpose"),
            complaints=anamnesis_data.get("complaints"),
            anamnesis=anamnesis_data.get("anamnesis")
        )
        
        logger.info(f"Анамнез успешно извлечён и сохранён: audio_id={audio_id}, appointment_id={appointment_id}")
        
        return report
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Ошибка конфигурации при извлечении анамнеза: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка при извлечении анамнеза: audio_id={audio_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка извлечения анамнеза: {str(e)}")


@router.post("/extract-anamnesis-by-appointment", response_model=MedicalReportSchema)
async def extract_anamnesis_by_appointment(
    appointment_id: int = Query(..., description="ID приёма"),
    db: AsyncSession = Depends(get_db)
):
    """Извлечь анамнез по appointment_id (вспомогательный endpoint)"""
    logger.info(f"Запрос извлечения анамнеза по приёму: appointment_id={appointment_id}")
    
    try:
        # Находим аудиофайл по appointment_id
        audio = await crud.get_audio_file_by_appointment(db, appointment_id)
        if not audio:
            logger.warning(f"Аудиофайл не найден для приёма: appointment_id={appointment_id}")
            raise HTTPException(status_code=404, detail="Аудиофайл не найден для этого приёма")
        
        # Используем существующую логику
        return await extract_anamnesis_from_transcription(audio.id, db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при извлечении анамнеза по приёму: appointment_id={appointment_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка извлечения анамнеза: {str(e)}")


@router.delete("/by-appointment/{appointment_id}")
async def delete_audio_by_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить аудиофайл и транскрипцию для приёма"""
    logger.info(f"Запрос на удаление аудио для приёма: appointment_id={appointment_id}")
    
    # Находим аудиофайл
    audio = await crud.get_audio_file_by_appointment(db, appointment_id)
    if not audio:
        raise HTTPException(status_code=404, detail="Аудиофайл не найден для этого приёма")
    
    # Удаляем физический файл, если он существует
    if audio.filepath and os.path.exists(audio.filepath):
        try:
            os.remove(audio.filepath)
            logger.info(f"Физический файл удалён: {audio.filepath}")
        except Exception as e:
            logger.warning(f"Не удалось удалить физический файл: {e}")
    
    # Удаляем запись из БД
    await crud.delete_audio_file(db, audio.id)
    logger.info(f"Аудиофайл удалён из БД: audio_id={audio.id}, appointment_id={appointment_id}")
    
    return {"success": True, "message": "Аудиофайл успешно удалён"}


@router.post("/mock-transcription")
async def create_mock_transcription(
    appointment_id: int = Query(..., description="ID приёма"),
    db: AsyncSession = Depends(get_db)
):
    """
    Имитация транскрибации - загрузка текста из talk.md
    Для демо-презентации: создаёт иллюзию реальной обработки аудио
    """
    logger.info(f"Запрос mock-транскрипции для приёма: appointment_id={appointment_id}")
    
    try:
        # Проверяем, существует ли приём
        appointment = await crud.get_appointment(db, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Приём не найден")
        
        # Сначала пытаемся получить текст из БД (тестовые данные)
        transcription_text = None
        test_data = await crud.get_test_data(db, key="transcription_text")
        if test_data and test_data.content:
            transcription_text = test_data.content
            logger.info("Использованы тестовые данные из БД")
        else:
            # Fallback: читаем текст из файла talk.md
            talk_file_path = Path("data/talk.md")
            if talk_file_path.exists():
                with open(talk_file_path, "r", encoding="utf-8") as f:
                    transcription_text = f.read()
                logger.info("Использован файл talk.md")
            else:
                logger.error("Файл talk.md не найден и нет данных в БД")
                raise HTTPException(status_code=500, detail="Файл стенограммы не найден")
        
        if not transcription_text:
            raise HTTPException(status_code=500, detail="Текст стенограммы пуст")
        
        # Проверяем, не создан ли уже аудиофайл
        existing_audio = await crud.get_audio_file_by_appointment(db, appointment_id)
        
        if not existing_audio:
            # Создаём "виртуальный" аудиофайл
            audio = await crud.create_audio_file(
                db,
                appointment_id=appointment_id,
                filename="mock_recording.wav",
                filepath="",
                file_size=len(transcription_text.encode('utf-8')),
                mime_type="audio/wav"
            )
        else:
            audio = existing_audio
        
        # Обновляем транскрипцию
        audio = await crud.update_transcription(
            db,
            audio.id,
            TranscriptionStatus.COMPLETED,
            text=transcription_text
        )
        
        logger.info(f"Mock-транскрипция успешно создана: appointment_id={appointment_id}")
        
        return TranscriptionResponse(
            success=True,
            message="Транскрибация успешно завершена",
            transcription_status=audio.transcription_status,
            transcription_text=audio.transcription_text,
            transcribed_at=audio.transcribed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка mock-транскрипции: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка транскрибации: {str(e)}")

