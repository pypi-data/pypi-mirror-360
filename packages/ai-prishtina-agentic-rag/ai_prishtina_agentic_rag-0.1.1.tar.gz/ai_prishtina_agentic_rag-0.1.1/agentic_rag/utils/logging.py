"""Logging utilities for the Agentic RAG library."""

import logging
import sys
from pathlib import Path
from typing import Optional, Union

import structlog
from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    level: Union[str, int] = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    enable_rich: bool = True,
    enable_structlog: bool = True,
) -> None:
    """
    Set up logging configuration for the Agentic RAG library.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        enable_rich: Whether to use rich formatting for console output
        enable_structlog: Whether to use structured logging
    """
    # Convert string level to logging constant
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # Configure handlers
    handlers = []
    
    # Console handler
    if enable_rich:
        console = Console(stderr=True)
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True,
        )
    else:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
    
    console_handler.setLevel(level)
    handlers.append(console_handler)
    
    # File handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
        )
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,
    )
    
    # Configure structlog if enabled
    if enable_structlog:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    # Suppress noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def get_structlog_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get a logger instance for this class."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    @property
    def struct_logger(self) -> structlog.BoundLogger:
        """Get a structured logger instance for this class."""
        return get_structlog_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")


# Performance logging utilities
class PerformanceLogger:
    """Utility class for performance logging."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._timers = {}
    
    def start_timer(self, name: str) -> None:
        """Start a performance timer."""
        import time
        self._timers[name] = time.time()
        self.logger.debug(f"Started timer: {name}")
    
    def end_timer(self, name: str) -> float:
        """End a performance timer and log the duration."""
        import time
        if name not in self._timers:
            self.logger.warning(f"Timer '{name}' was not started")
            return 0.0
        
        duration = time.time() - self._timers[name]
        del self._timers[name]
        
        self.logger.info(f"Timer '{name}' completed in {duration:.3f}s")
        return duration
    
    def log_memory_usage(self, context: str = "") -> None:
        """Log current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.logger.info(f"Memory usage{' (' + context + ')' if context else ''}: {memory_mb:.1f} MB")
        except ImportError:
            self.logger.warning("psutil not available for memory logging")


def log_function_call(func):
    """Decorator to log function calls with arguments and return values."""
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Log function entry
        args_str = ", ".join([str(arg) for arg in args])
        kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))
        
        logger.debug(f"Calling {func.__name__}({all_args})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {type(result).__name__}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
            raise
    
    return wrapper
