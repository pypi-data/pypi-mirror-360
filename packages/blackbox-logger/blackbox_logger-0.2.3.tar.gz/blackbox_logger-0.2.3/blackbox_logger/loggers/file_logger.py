# blackbox_logger/loggers/file_logger.py

import os
import logging
from logging.handlers import RotatingFileHandler

DEFAULT_LOG_DIR = "log"
DEFAULT_LOG_FILE = "blackbox.log"
MAX_LOG_FILE_SIZE = int(os.getenv("BLACKBOX_LOG_MAX_SIZE", 5 * 1024 * 1024))  # 5MB default
BACKUP_COUNT = int(os.getenv("BLACKBOX_LOG_BACKUP_COUNT", 3))

def setup_file_logger(log_dir=DEFAULT_LOG_DIR, log_file=DEFAULT_LOG_FILE):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger("blackbox_file_logger")
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        handler = RotatingFileHandler(log_path, maxBytes=MAX_LOG_FILE_SIZE, backupCount=BACKUP_COUNT)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    try:
        os.chmod(log_path, 0o664)
    except OSError as e:
        print(f"Error setting permissions: {e}")

    return logger