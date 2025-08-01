from booking_scheduler import BookingScheduler
from communication import SmsSender, MailSender
from datetime import datetime

class MockSmsSender(SmsSender):
    def __init__(self):
        super().__init__()
        self._send_called = False

    def send(self, schedule):
        print("테스트용SmsSender에서send 메서드실행됨")
        self._send_called = True

    @property
    def send_called(self) -> bool:
        return self._send_called


class MockMailSender(MailSender):
    def __init__(self):
        self._send_mail_count = 0

    def send_mail(self, schedule):
        self._send_mail_count += 1

    @property
    def send_mail_count(self) -> int:
        return self._send_mail_count
class MockScheduler(BookingScheduler):
    def __init__(self, capacity_per_hour, datetime_str):
        super().__init__(capacity_per_hour)
        self._datetime_str = datetime_str
    def get_now(self):
        return datetime.strptime(self._datetime_str, '%Y-%m-%d %H:%M')
class SundayBookingScheduler(BookingScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def get_now(self):
        return datetime.strptime('2025-08-03 00:00', '%Y-%m-%d %H:%M')
class MondayBookingScheduler(BookingScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def get_now(self):
        return datetime.strptime('2025-08-04 00:00', '%Y-%m-%d %H:%M')