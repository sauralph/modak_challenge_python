import os
import redis
from datetime import datetime, timedelta

class RateLimitExceededException(Exception):
    pass

class NotificationService:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        self.rate_limits = {
            'status': (2, 60),      # max 2 per minute
            'news': (1, 86400),     # max 1 per day
            'marketing': (3, 3600)  # max 3 per hour
        }

    def send(self, notification_type, recipient, message):
        if notification_type not in self.rate_limits:
            raise ValueError("Unknown notification type")

        max_count, period = self.rate_limits[notification_type]
        now = datetime.now()

        # Redis key for the recipient and notification type
        key = f"{recipient}:{notification_type}"
        
        # Clean up old notifications and check rate limit
        pipeline = self.redis_client.pipeline()
        pipeline.zremrangebyscore(key, 0, now.timestamp() - period)
        pipeline.zcard(key)
        results = pipeline.execute()

        count = results[1]
        if count >= max_count:
            raise RateLimitExceededException(
                f"Rate limit exceeded for {notification_type} to {recipient}"
            )

        # Send notification
        self._send_notification(recipient, message)
        self._log_notification(key, now.timestamp())

    def _log_notification(self, key, timestamp):
        pipeline = self.redis_client.pipeline()
        pipeline.zadd(key, {timestamp: timestamp})
        pipeline.expire(key, 86400)  # Ensure the key expires after one day to prevent unnecessary accumulation
        pipeline.execute()

    def _send_notification(self, recipient, message):
        print(f"Sending '{message}' to {recipient}")

# Example usage
if __name__ == "__main__":
    service = NotificationService(
        redis_host=os.getenv('REDIS_HOST', 'localhost'),
        redis_port=int(os.getenv('REDIS_PORT', 6379))
    )

    try:
        service.send("status", "user1@example.com", "Status update 1")
        service.send("status", "user1@example.com", "Status update 2")
        service.send("status", "user1@example.com", "Status update 3")  # This should raise an exception
    except RateLimitExceededException as e:
        print(e)

    try:
        service.send("news", "user2@example.com", "Daily news")
        service.send("news", "user2@example.com", "Another news")  # This should raise an exception
    except RateLimitExceededException as e:
        print(e)