# tasks.py
from celery import Celery
from time import sleep
import logging

logger = logging.getLogger(__name__)

CELERY_BROKER_URL = "redis://localhost:6380/0"
CELERY_RESULT_BACKEND = "redis://localhost:6380/1"

celery = Celery(
    "config",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@celery.task
def notify_new_stock(ticker: str, stock_name: str, stock_price: float):
    """Simulate sending a notification when a new book is created."""
    logger.info(f"New book created: ticker='{ticker}', name='{stock_name}',price={stock_price} ")
    # Simulate a delay for the notification process
    sleep(2)
    logger.info(f"Notification for stock '{ticker}' sent successfully.")
