"""Настройка системы логирования приложения"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from app.config import settings


class CustomFormatter(logging.Formatter):
    """Кастомный форматтер с цветами для консоли"""
    
    # Цветовые коды ANSI
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: blue + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class DailyRotatingFileHandler(TimedRotatingFileHandler):
    """Handler с ротацией логов по дням и датой в названии файла"""
    
    def __init__(self, log_dir: Path, filename_prefix: str, **kwargs):
        """
        Args:
            log_dir: Директория для логов
            filename_prefix: Префикс имени файла (например, 'app' или 'access')
        """
        self.log_dir = log_dir
        self.filename_prefix = filename_prefix
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем имя файла с текущей датой
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = self.log_dir / f"{filename_prefix}-{current_date}.log"
        
        # Инициализируем родительский класс с ротацией в полночь
        super().__init__(
            filename=str(filename),
            when='midnight',
            interval=1,
            backupCount=settings.log_retention_days,
            encoding='utf-8',
            **kwargs
        )
        
    def doRollover(self):
        """Переопределяем для создания файла с датой в названии"""
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # Создаем новое имя файла с новой датой
        current_date = datetime.now().strftime("%Y-%m-%d")
        new_filename = self.log_dir / f"{self.filename_prefix}-{current_date}.log"
        self.baseFilename = str(new_filename)
        
        # Удаляем старые логи если превышен лимит
        self.delete_old_logs()
        
        # Открываем новый файл
        if not self.delay:
            self.stream = self._open()
    
    def delete_old_logs(self):
        """Удаляет старые лог-файлы"""
        if self.backupCount > 0:
            log_files = sorted(
                self.log_dir.glob(f"{self.filename_prefix}-*.log"),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            
            # Удаляем файлы старше backupCount дней
            for old_file in log_files[self.backupCount:]:
                try:
                    old_file.unlink()
                except Exception as e:
                    print(f"Ошибка при удалении старого лога {old_file}: {e}")


def setup_logging(
    app_name: str = "elia",
    log_level: Optional[str] = None
) -> logging.Logger:
    """
    Настройка системы логирования
    
    Args:
        app_name: Имя приложения для логов
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Настроенный корневой логгер
    """
    # Определяем уровень логирования
    if log_level is None:
        log_level = settings.log_level
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Создаем директорию для логов
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Получаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Очищаем существующие handlers
    root_logger.handlers.clear()
    
    # === 1. Консольный handler (с цветами) ===
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(console_handler)
    
    # === 2. Файловый handler для всех логов ===
    app_file_handler = DailyRotatingFileHandler(
        log_dir=log_dir,
        filename_prefix=f"{app_name}-app"
    )
    app_file_handler.setLevel(numeric_level)
    file_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    app_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(app_file_handler)
    
    # === 3. Отдельный handler для ошибок ===
    error_file_handler = DailyRotatingFileHandler(
        log_dir=log_dir,
        filename_prefix=f"{app_name}-errors"
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_file_handler)
    
    # === 4. Handler для access логов (HTTP запросы) ===
    access_file_handler = DailyRotatingFileHandler(
        log_dir=log_dir,
        filename_prefix=f"{app_name}-access"
    )
    access_file_handler.setLevel(logging.INFO)
    access_formatter = logging.Formatter(
        fmt='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    access_file_handler.setFormatter(access_formatter)
    
    # Создаем отдельный логгер для access логов
    access_logger = logging.getLogger("elia.access")
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False  # Не передаем в корневой логгер
    access_logger.addHandler(access_file_handler)
    
    # Настраиваем уровни для библиотек
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Логируем успешную инициализацию
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование настроено: уровень={log_level}, директория={log_dir}")
    logger.info(f"Логи будут храниться {settings.log_retention_days} дней")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер для модуля
    
    Args:
        name: Имя модуля (обычно __name__)
    
    Returns:
        Настроенный логгер
    """
    return logging.getLogger(name)


# Специальный логгер для access логов
def get_access_logger() -> logging.Logger:
    """Получить логгер для HTTP access логов"""
    return logging.getLogger("elia.access")

