import logging
import json
import threading
from datetime import datetime
import uuid

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("system.log")

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "thread": record.threadName,
            "level": record.levelname,
            "message": record.msg,
        }

        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        return json.dumps(log_record)

handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

def log_event(message, **kwargs):
    logger.info(
        message,
        extra={"extra_data": kwargs}
    )


def create_trace():
    return str(uuid.uuid4())

def shutdown_logger():
    logger.removeHandler(handler)
    logging.shutdown() 