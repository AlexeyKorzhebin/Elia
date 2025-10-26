"""Сервис для работы с OpenAI API"""
import json
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Сервис для работы с OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI"""
        if not settings.openai_api_key:
            logger.warning("OpenAI API key не настроен")
            self.client = None
        else:
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
    
    async def generate_conversation(self, patient_name: str, patient_age: int, patient_gender: str) -> str:
        """
        Генерация диалога врач-пациент с временными метками
        
        Args:
            patient_name: ФИО пациента
            patient_age: Возраст пациента
            patient_gender: Пол пациента (male/female)
        
        Returns:
            Транскрипция диалога с временными метками
        """
        if not self.client:
            raise ValueError("OpenAI API key не настроен. Проверьте файл .env")
        
        gender_ru = "мужчина" if patient_gender == "male" else "женщина"
        
        system_prompt = """Ты - эксперт по созданию медицинских транскрипций. 
Твоя задача - создать реалистичный диалог между врачом и пациентом на приёме в поликлинике.

Требования:
1. Диалог должен длиться 5-7 минут
2. Каждая реплика должна иметь временную метку в формате MM:SS
3. Диалог должен быть естественным и реалистичным
4. Включить основные этапы приёма: приветствие, сбор жалоб, анамнез, осмотр, рекомендации
5. Использовать профессиональную медицинскую терминологию, но доступным языком
6. Диалог должен быть на русском языке

Формат вывода:
00:00 - Врач: [текст]
00:15 - Пациент: [текст]
..."""

        user_prompt = f"""Создай транскрипцию диалога врача с пациентом.

Информация о пациенте:
- ФИО: {patient_name}
- Возраст: {patient_age} лет
- Пол: {gender_ru}

Создай реалистичный медицинский диалог с конкретной проблемой со здоровьем. 
Диалог должен включать жалобы пациента, сбор анамнеза, осмотр и рекомендации врача."""

        try:
            logger.info(f"Запрос генерации диалога для пациента: {patient_name}")
            
            # Формируем параметры запроса
            request_params = {
                "model": settings.openai_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_completion_tokens": 2000
            }
            
            # Добавляем temperature только если модель поддерживает
            # gpt-5-mini не поддерживает кастомные значения temperature
            if "gpt-5" not in settings.openai_model.lower():
                request_params["temperature"] = 0.8
            
            response = await self.client.chat.completions.create(**request_params)
            
            conversation = response.choices[0].message.content.strip()
            
            logger.info(f"Диалог успешно сгенерирован, длина: {len(conversation)} символов")
            
            return conversation
            
        except Exception as e:
            logger.error(f"Ошибка при генерации диалога: {str(e)}")
            raise
    
    async def extract_anamnesis_data(self, transcription: str) -> Dict[str, Optional[str]]:
        """
        Извлечение структурированных данных из транскрипции для анамнеза
        
        Args:
            transcription: Текст транскрипции диалога
        
        Returns:
            Словарь с полями: purpose, complaints, anamnesis
        """
        if not self.client:
            raise ValueError("OpenAI API key не настроен. Проверьте файл .env")
        
        system_prompt = """Ты - медицинский ассистент, специализирующийся на структурировании медицинской информации.
Твоя задача - проанализировать транскрипцию диалога врача с пациентом и извлечь структурированные данные для медицинской карты.

Верни ответ СТРОГО в формате JSON со следующими полями:
{
  "purpose": "Краткая цель обращения (1-2 предложения)",
  "complaints": "Основные жалобы пациента (детально, как он описывал)",
  "anamnesis": "Подробный анамнез: история заболевания, результаты осмотра, предварительный диагноз, назначения и рекомендации"
}

Требования:
1. purpose - краткая суть обращения
2. complaints - все жалобы пациента своими словами
3. anamnesis - полная информация: когда началось, как развивалось, данные осмотра, диагноз, назначения
4. Используй профессиональную медицинскую терминологию
5. Будь кратким, но информативным"""

        user_prompt = f"""Проанализируй следующую транскрипцию диалога врача с пациентом и извлеки структурированные данные:

{transcription}

Верни данные в формате JSON."""

        try:
            logger.info("Запрос извлечения данных анамнеза из транскрипции")
            
            # Формируем параметры запроса
            request_params = {
                "model": settings.openai_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_completion_tokens": 1500,
                "response_format": {"type": "json_object"}
            }
            
            # Добавляем temperature только если модель поддерживает
            # gpt-5-mini не поддерживает кастомные значения temperature
            if "gpt-5" not in settings.openai_model.lower():
                request_params["temperature"] = 0.3
            
            response = await self.client.chat.completions.create(**request_params)
            
            content = response.choices[0].message.content.strip()
            
            # Парсим JSON ответ
            data = json.loads(content)
            
            # Проверяем наличие обязательных полей
            result = {
                "purpose": data.get("purpose"),
                "complaints": data.get("complaints"),
                "anamnesis": data.get("anamnesis")
            }
            
            logger.info("Данные анамнеза успешно извлечены")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON ответа: {str(e)}")
            raise ValueError("Не удалось распарсить ответ от OpenAI")
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных анамнеза: {str(e)}")
            raise


# Singleton экземпляр
openai_service = OpenAIService()

