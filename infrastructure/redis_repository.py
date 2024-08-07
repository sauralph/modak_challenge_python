import redis
from datetime import datetime, timedelta

class RedisRepository:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    def cleanup_old_notifications(self, recipient, notification_type, period, now):
        key = f"{recipient}:{notification_type}"
        self.redis_client.zremrangebyscore(key, 0, now.timestamp() - period)

    def get_notification_count(self, recipient, notification_type, period, now):
        key = f"{recipient}:{notification_type}"
        cutoff = now - timedelta(seconds=period)
        return self.redis_client.zcard(key)

    def log_notification(self, recipient, notification_type, timestamp):
        key = f"{recipient}:{notification_type}"
        self.redis_client.zadd(key, {timestamp.timestamp(): timestamp.timestamp()})
        self.redis_client.expire(key, 86400)
        
    def clear_all_notifications(self):
        keys = self.redis_client.keys('*:*')
        if keys:
            self.redis_client.delete(*keys)
