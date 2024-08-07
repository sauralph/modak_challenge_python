import os
from domain.notification import NotificationService
from application.services import NotificationServiceApp
from infrastructure.redis_repository import RedisRepository
from app.config import rate_limits_config

def get_notification_service_app():
    redis_repository = RedisRepository(
        redis_host=os.getenv('REDIS_HOST', 'localhost'),
        redis_port=int(os.getenv('REDIS_PORT', 6379))
    )
    rate_limits = {
        'status': (rate_limits_config.status_count, rate_limits_config.status_period),
        'news': (rate_limits_config.news_count, rate_limits_config.news_period),
        'marketing': (rate_limits_config.marketing_count, rate_limits_config.marketing_period)
    }
    notification_service = NotificationService(redis_repository, rate_limits)
    return NotificationServiceApp(notification_service)
