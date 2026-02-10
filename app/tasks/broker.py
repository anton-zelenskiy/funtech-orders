from taskiq_redis import ListQueueBroker

from app.core.config import settings
from app.core.logging import setup_logging

setup_logging(log_level=settings.log_level)

broker = ListQueueBroker(url=settings.redis_url)
