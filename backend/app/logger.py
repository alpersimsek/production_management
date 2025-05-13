import logging
import json
from datetime import datetime
import os

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

logger = logging.getLogger("gdpr")
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logging

# Console handler with colored output
console_handler = logging.StreamHandler()
console_handler.setFormatter(StructuredFormatter())
logger.addHandler(console_handler)

# File handler with plain JSON output
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, "gdpr.log"))
file_handler.setFormatter(PlainStructuredFormatter())
logger.addHandler(file_handler)

logger.propagate = False