"""Logging utilities for Grasp SDK Python implementation.

This module provides a structured logging system with support for
different log levels, console output, and file logging.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Union
from enum import IntEnum


class LogLevel(IntEnum):
    """Log levels with numeric values for comparison."""
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


class Logger:
    """Logger class for structured logging."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize logger with configuration.
        
        Args:
            config: Logger configuration dictionary containing:
                   - level: Log level ('debug', 'info', 'warn', 'error')
                   - console: Whether to output to console
                   - file: Optional file path for logging
        """
        self.config = config
        self.current_level = LogLevel[config['level'].upper()]
        self._setup_file_logger()
    
    def _setup_file_logger(self) -> None:
        """Setup file logging if configured."""
        if self.config.get('file'):
            # Configure Python's built-in logging for file output
            logging.basicConfig(
                filename=self.config['file'],
                level=getattr(logging, self.config['level'].upper()),
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%dT%H:%M:%S.%fZ'
            )
            self.file_logger = logging.getLogger('grasp_file')
        else:
            self.file_logger = None
    
    def _format_message(self, level: str, message: str, data: Optional[Any] = None) -> str:
        """Formats log message with timestamp and level.
        
        Args:
            level: Log level string
            message: Log message
            data: Additional data to log
            
        Returns:
            str: Formatted log string
        """
        timestamp = datetime.utcnow().isoformat() + 'Z'
        data_str = f' {json.dumps(data)}' if data is not None else ''
        return f'[{timestamp}] [{level.upper()}] {message}{data_str}'
    
    def _log(self, level: str, message: str, data: Optional[Any] = None) -> None:
        """Logs a message if the level is enabled.
        
        Args:
            level: Log level string
            message: Log message
            data: Additional data to log
        """
        level_enum = LogLevel[level.upper()]
        if level_enum < self.current_level:
            return
        
        formatted_message = self._format_message(level, message, data)
        
        # Console output
        if self.config['console']:
            if level == 'debug':
                print(formatted_message, file=sys.stdout)
            elif level == 'info':
                print(formatted_message, file=sys.stdout)
            elif level == 'warn':
                print(formatted_message, file=sys.stderr)
            elif level == 'error':
                print(formatted_message, file=sys.stderr)
        
        # File output
        if self.file_logger:
            if level == 'debug':
                self.file_logger.debug(message, extra={'data': data} if data else None)
            elif level == 'info':
                self.file_logger.info(message, extra={'data': data} if data else None)
            elif level == 'warn':
                self.file_logger.warning(message, extra={'data': data} if data else None)
            elif level == 'error':
                self.file_logger.error(message, extra={'data': data} if data else None)
    
    def debug(self, message: str, data: Optional[Any] = None) -> None:
        """Logs debug message.
        
        Args:
            message: Debug message
            data: Additional data
        """
        self._log('debug', message, data)
    
    def info(self, message: str, data: Optional[Any] = None) -> None:
        """Logs info message.
        
        Args:
            message: Info message
            data: Additional data
        """
        self._log('info', message, data)
    
    def warn(self, message: str, data: Optional[Any] = None) -> None:
        """Logs warning message.
        
        Args:
            message: Warning message
            data: Additional data
        """
        self._log('warn', message, data)
    
    def error(self, message: str, data: Optional[Any] = None) -> None:
        """Logs error message.
        
        Args:
            message: Error message
            data: Additional data
        """
        self._log('error', message, data)
    
    def child(self, context: str) -> 'Logger':
        """Creates a child logger with additional context.
        
        Args:
            context: Context to add to all log messages
            
        Returns:
            Logger: New logger instance with context
        """
        child_logger = Logger(self.config)
        
        # Override the _log method to add context
        original_log = child_logger._log
        
        def contextual_log(level: str, message: str, data: Optional[Any] = None) -> None:
            original_log(level, f'[{context}] {message}', data)
        
        child_logger._log = contextual_log
        return child_logger


# Global logger instance
_default_logger: Optional[Logger] = None


def init_logger(config: Dict[str, Any]) -> None:
    """Initializes the default logger.
    
    Args:
        config: Logger configuration dictionary
    """
    global _default_logger
    _default_logger = Logger(config)


def get_logger() -> Logger:
    """Gets the default logger instance.
    
    Returns:
        Logger: Default logger instance
        
    Raises:
        RuntimeError: If logger is not initialized
    """
    if _default_logger is None:
        raise RuntimeError('Logger not initialized. Call init_logger() first.')
    return _default_logger


def get_default_logger() -> Logger:
    """Gets a default logger with basic configuration.
    
    Returns:
        Logger: Logger with default configuration
    """
    default_config = {
        'level': 'info',
        'console': True,
        'file': None,
    }
    return Logger(default_config)


# Convenience functions for quick logging
def debug(message: str, data: Optional[Any] = None) -> None:
    """Quick debug logging function."""
    try:
        get_logger().debug(message, data)
    except RuntimeError:
        get_default_logger().debug(message, data)


def info(message: str, data: Optional[Any] = None) -> None:
    """Quick info logging function."""
    try:
        get_logger().info(message, data)
    except RuntimeError:
        get_default_logger().info(message, data)


def warn(message: str, data: Optional[Any] = None) -> None:
    """Quick warning logging function."""
    try:
        get_logger().warn(message, data)
    except RuntimeError:
        get_default_logger().warn(message, data)


def error(message: str, data: Optional[Any] = None) -> None:
    """Quick error logging function."""
    try:
        get_logger().error(message, data)
    except RuntimeError:
        get_default_logger().error(message, data)