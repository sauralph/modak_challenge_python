import os
from domain.notification import NotificationService
from application.services import NotificationServiceApp
from infrastructure.redis_repository import RedisRepository

def get_rate_limit(env_var_name, default_value):
    return int(os.getenv(env_var_name, default_value))

def get_notification_service_app():
    redis_repository = RedisRepository(
        redis_host=os.getenv('REDIS_HOST', 'localhost'),
        redis_port=int(os.getenv('REDIS_PORT', 6379))
    )
    rate_limits = {
        'status': (get_rate_limit('STATUS_LIMIT_COUNT', 2), get_rate_limit('STATUS_LIMIT_PERIOD', 60)),      # max 2 per minute
        'news': (get_rate_limit('NEWS_LIMIT_COUNT', 1), get_rate_limit('NEWS_LIMIT_PERIOD', 86400)),         # max 1 per day
        'marketing': (get_rate_limit('MARKETING_LIMIT_COUNT', 3), get_rate_limit('MARKETING_LIMIT_PERIOD', 3600))  # max 3 per hour
    }
    notification_service = NotificationService(redis_repository, rate_limits)
    return NotificationServiceApp(notification_service)
