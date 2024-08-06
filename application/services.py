class NotificationServiceApp:
    def __init__(self, notification_service):
        self.notification_service = notification_service

    def send_notification(self, notification_type, recipient, message):
        self.notification_service.send(notification_type, recipient, message)
