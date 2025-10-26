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
    TranscriptionResponse
)

router = APIRouter(prefix="/api/audio", tags=["audio"])

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

