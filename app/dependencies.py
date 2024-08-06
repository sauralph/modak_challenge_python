import os
from domain.notification import NotificationService
from application.services import NotificationServiceApp
from infrastructure.redis_repository import RedisRepository

def get_notification_service_app():
    redis_repository = RedisRepository(
        redis_host=os.getenv('REDIS_HOST', 'localhost'),
        redis_port=int(os.getenv('REDIS_PORT', 6379))
    )
    rate_limits = {
        'status': (2, 60),      # max 2 per minute
        'news': (1, 86400),     # max 1 per day
        'marketing': (3, 3600)  # max 3 per hour
    }
    notification_service = NotificationService(redis_repository, rate_limits)
    return NotificationServiceApp(notification_service)
