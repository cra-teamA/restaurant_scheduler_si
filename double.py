from booking_scheduler import BookingScheduler
from communication import SmsSender, MailSender
from datetime import datetime

class MockBookingScheduler(BookingScheduler):
    def __init__(self, capacity_per_hour, datetime_str):
        super().__init__(capacity_per_hour)
        self._datetime_str = datetime_str
    def get_now(self):
        return datetime.strptime(self._datetime_str, '%Y-%m-%d %H:%M')
