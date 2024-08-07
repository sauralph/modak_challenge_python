from datetime import datetime, timedelta
from domain.exceptions import RateLimitExceededException

class NotificationService:
    def __init__(self, repository, rate_limits):
        self.repository = repository
        self.rate_limits = rate_limits

    def send(self, notification_type, recipient, message):
        if notification_type not in self.rate_limits:
            raise ValueError("Unknown notification type")

        max_count, period = self.rate_limits[notification_type]
        now = datetime.now()

        # Clean up old notifications and check rate limit
        self.repository.cleanup_old_notifications(recipient, notification_type, period, now)
        count = self.repository.get_notification_count(recipient, notification_type, period, now)

        if count >= max_count:
            raise RateLimitExceededException(
                f"Rate limit exceeded for {notification_type} to {recipient}"
            )

        # Send notification
        self._send_notification(recipient, message)
        self.repository.log_notification(recipient, notification_type, now)

    def _send_notification(self, recipient, message):
        print(f"Sending '{message}' to {recipient}")

    def clean_all_notifications(self):
        self.repository.clean_all_notifications()

