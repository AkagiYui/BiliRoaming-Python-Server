import re
from logging import DEBUG, INFO, Logger, StreamHandler, getLogger
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from uvicorn.logging import DefaultFormatter


def create_logger() -> Logger:
    """创建日志记录器"""
    logger: Logger = getLogger('biliroaming')
    logger.setLevel(DEBUG)
    logger.addHandler(StreamHandler())
    logger.handlers[0].setFormatter(DefaultFormatter(fmt='%(levelprefix)s %(message)s'))
    return logger


def create_request_logger() -> Logger:
    """创建请求日志记录器"""
    logger = getLogger('request')
    logger.setLevel(INFO)
    parent_dir = Path(__file__).resolve().parent / 'logs'
    if not parent_dir.exists():
        parent_dir.mkdir(parents=True, exist_ok=True)
    handler = TimedRotatingFileHandler(
        filename=parent_dir / 'request.log',
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8',
    )
    handler.suffix = '%Y-%m-%d_%H-%M.log'
    handler.extMatch = re.compile(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$')
    handler.setFormatter(DefaultFormatter(fmt='%(asctime)s %(message)s'))
    logger.addHandler(handler)
    return logger


log = create_logger()
request_logger = create_request_logger()
