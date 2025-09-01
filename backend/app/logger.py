"""
GDPR Tool Logger - Structured Logging System

This module provides a comprehensive structured logging system for the GDPR compliance tool.
It implements JSON-formatted logging with colorized console output and automatic log rotation.

Key Features:
- Structured Logging: All log entries are formatted as JSON for easy parsing and analysis
- Colorized Console Output: Different log levels are displayed in different colors for better readability
- Log Rotation: Automatic rotation of log files when they reach 3MB with up to 10 backup files
- Log Cleanup: Automatic deletion of log files older than 30 days to manage disk space
- Context Support: Additional context information can be attached to log entries
- Dual Output: Logs are written to both console (with colors) and file (plain JSON)

Log Levels:
- DEBUG: Detailed information for debugging (Blue)
- INFO: General information about program execution (Green)
- WARNING: Warning messages for potential issues (Yellow)
- ERROR: Error messages for recoverable errors (Red)
- CRITICAL: Critical errors that may cause program termination (Magenta)

Log Structure:
Each log entry contains:
- timestamp: ISO format timestamp
- level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- message: The log message
- module: Python module name where the log was generated
- funcName: Function name where the log was generated
- line: Line number where the log was generated
- context: Additional context data (if provided)

Usage:
```python
from logger import logger

# Basic logging
logger.info("Processing started")
logger.error("Processing failed", extra={"context": {"file_id": "123"}})

# With context
logger.debug("File processed", extra={"context": {"file_id": "123", "size": 1024}})
```

The logger is configured to write to both console and file, with automatic rotation
and cleanup to ensure efficient log management in production environments.
"""

import logging
import json
from datetime import datetime, timedelta
import os
import glob
import time
from logging.handlers import RotatingFileHandler

# ANSI color codes for console output
COLORS = {
    'DEBUG': '\033[94m',  # Blue
    'INFO': '\033[92m',   # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',  # Red
    'CRITICAL': '\033[95m',  # Magenta
    'RESET': '\033[0m'    # Reset color
}

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "context"):
            log_entry.update(record.context)
        log_message = json.dumps(log_entry)
        color = COLORS.get(record.levelname, '')
        reset = COLORS['RESET']
        return f"{color}{log_message}{reset}"

class PlainStructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "context"):
            log_entry.update(record.context)
        return json.dumps(log_entry)

def cleanup_old_logs(log_dir: str, max_age_days: int = 30):
    """Delete log files older than max_age_days in log_dir."""
    max_age_seconds = max_age_days * 24 * 60 * 60  # Convert days to seconds
    current_time = time.time()
    log_pattern = os.path.join(log_dir, "gdpr.log*")  # Match gdpr.log and rotated files
    for log_file in glob.glob(log_pattern):
        try:
            file_mtime = os.path.getmtime(log_file)
            file_age = current_time - file_mtime
            if file_age > max_age_seconds:
                os.unlink(log_file)
                logging.getLogger("gdpr").debug({
                    "event": "log_file_deleted",
                    "file_path": log_file,
                    "age_days": file_age / (24 * 60 * 60),
                })
        except Exception as e:
            logging.getLogger("gdpr").warning({
                "event": "log_cleanup_failed",
                "file_path": log_file,
                "error": str(e),
            })

logger = logging.getLogger("gdpr")
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logging

# Console handler with colored output
console_handler = logging.StreamHandler()
console_handler.setFormatter(StructuredFormatter())
logger.addHandler(console_handler)

# File handler with rotation at 3MB
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
file_handler = RotatingFileHandler(
    os.path.join(log_dir, "gdpr.log"),
    maxBytes=3 * 1024 * 1024,  # 3MB
    backupCount=10,  # Keep up to 10 rotated files
)
file_handler.setFormatter(PlainStructuredFormatter())
logger.addHandler(file_handler)

# Cleanup old logs during initialization
cleanup_old_logs(log_dir, max_age_days=30)

logger.propagate = False