import sqlite3
from datetime import datetime, timedelta

class RateLimitExceededException(Exception):
    pass

class NotificationService:
    def __init__(self, db_name="notifications.db"):
        self.db_name = db_name
        self._initialize_database()
        self._initialize_rate_limits()

    def _initialize_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rate_limits (
                    notification_type TEXT PRIMARY KEY,
                    max_count INTEGER NOT NULL,
                    period_seconds INTEGER NOT NULL
                )
            ''')
            conn.commit()

    def _initialize_rate_limits(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO rate_limits (notification_type, max_count, period_seconds)
                VALUES
                ('status', 2, ?),
                ('news', 1, ?),
                ('marketing', 3, ?)
            ''', (60, 86400, 3600))
            conn.commit()

    def get_rate_limit(self, notification_type):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT max_count, period_seconds FROM rate_limits
                WHERE notification_type = ?
            ''', (notification_type,))
            result = cursor.fetchone()
            if result:
                max_count, period_seconds = result
                period = timedelta(seconds=period_seconds)
                return max_count, period
            else:
                raise ValueError(f"Unknown notification type: {notification_type}")

    def send(self, notification_type, recipient, message):
        max_count, period = self.get_rate_limit(notification_type)
        now = datetime.now()

        # Clean up old notifications
        self._cleanup_old_notifications(recipient, notification_type, period, now)

        # Check rate limit
        count = self._get_notification_count(recipient, notification_type, period, now)
        if count >= max_count:
            raise RateLimitExceededException(
                f"Rate limit exceeded for {notification_type} to {recipient}"
            )

        # Send notification
        self._send_notification(recipient, message)
        self._log_notification(recipient, notification_type, now)

    def _cleanup_old_notifications(self, recipient, notification_type, period, now):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cutoff = now - period
            cursor.execute('''
                DELETE FROM notifications
                WHERE recipient = ? AND notification_type = ? AND timestamp <= ?
            ''', (recipient, notification_type, cutoff))
            conn.commit()

    def _get_notification_count(self, recipient, notification_type, period, now):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cutoff = now - period
            cursor.execute('''
                SELECT COUNT(*) FROM notifications
                WHERE recipient = ? AND notification_type = ? AND timestamp > ?
            ''', (recipient, notification_type, cutoff))
            return cursor.fetchone()[0]

    def _log_notification(self, recipient, notification_type, timestamp):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (recipient, notification_type, timestamp)
                VALUES (?, ?, ?)
            ''', (recipient, notification_type, timestamp))
            conn.commit()

    def _send_notification(self, recipient, message):
        print(f"Sending '{message}' to {recipient}")

# Example usage
if __name__ == "__main__":
    service = NotificationService()

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
