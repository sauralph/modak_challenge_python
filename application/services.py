class NotificationServiceApp:
    def __init__(self, notification_service):
        self.notification_service = notification_service

    def send_notification(self, notification_type, recipient, message):
        # strip leading and trailing whitespaces
        recipient = recipient.strip()
        self.notification_service.send(notification_type, recipient, message)

    def clear_all_notifications(self):
        self.notification_service.clear_all_notifications()

    def get_all_usage(self):
        return self.notification_service.get_all_usage()
