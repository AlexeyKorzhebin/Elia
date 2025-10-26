"""Middleware для логирования запросов"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.logger import get_logger, get_access_logger

logger = get_logger(__name__)
access_logger = get_access_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов и ответов"""
    
    # Пути, которые не нужно логировать (чтобы не захламлять логи)
    EXCLUDE_PATHS = {
        "/health",
        "/static",
        "/favicon.ico"
    }
    
    # Заголовки, которые нужно скрыть (чувствительные данные)
    SENSITIVE_HEADERS = {
        "authorization",
        "cookie",
        "x-api-key",
        "x-auth-token"
    }
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с логированием"""
        
        # Пропускаем некоторые пути
        if any(request.url.path.startswith(path) for path in self.EXCLUDE_PATHS):
            return await call_next(request)
        
        # Начало обработки запроса
        start_time = time.time()
        
        # Получаем информацию о клиенте
        client_host = request.client.host if request.client else "unknown"
        
        # Логируем входящий запрос
        logger.debug(
            f"Входящий запрос: {request.method} {request.url.path} "
            f"от {client_host}"
        )
        
        # Обрабатываем запрос
        try:
            response = await call_next(request)
            
            # Вычисляем время обработки
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)
            
            # Логируем в access log
            access_logger.info(
                f"{client_host} - \"{request.method} {request.url.path}\" "
                f"{response.status_code} - {process_time_ms}ms"
            )
            
            # Детальное логирование в зависимости от статуса
            if response.status_code >= 500:
                logger.error(
                    f"Ошибка сервера: {request.method} {request.url.path} "
                    f"-> {response.status_code} ({process_time_ms}ms)"
                )
            elif response.status_code >= 400:
                logger.warning(
                    f"Ошибка клиента: {request.method} {request.url.path} "
                    f"-> {response.status_code} ({process_time_ms}ms)"
                )
            elif process_time > 1.0:  # Медленный запрос (> 1 секунды)
                logger.warning(
                    f"Медленный запрос: {request.method} {request.url.path} "
                    f"-> {response.status_code} ({process_time_ms}ms)"
                )
            else:
                logger.info(
                    f"Запрос обработан: {request.method} {request.url.path} "
                    f"-> {response.status_code} ({process_time_ms}ms)"
                )
            
            # Добавляем время обработки в заголовки ответа
            response.headers["X-Process-Time"] = str(process_time_ms)
            
            return response
            
        except Exception as e:
            # Логируем исключение
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)
            
            logger.exception(
                f"Необработанное исключение: {request.method} {request.url.path} "
                f"от {client_host} ({process_time_ms}ms): {str(e)}"
            )
            
            # Пробрасываем исключение дальше
            raise
    
    @staticmethod
    def sanitize_headers(headers: dict) -> dict:
        """Удаляет чувствительные заголовки из логов"""
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in LoggingMiddleware.SENSITIVE_HEADERS:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        return sanitized


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для перехвата и логирования всех ошибок"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с перехватом ошибок"""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Логируем полную информацию об ошибке
            logger.exception(
                f"Критическая ошибка при обработке {request.method} {request.url.path}",
                exc_info=True,
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "client": request.client.host if request.client else "unknown",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise

