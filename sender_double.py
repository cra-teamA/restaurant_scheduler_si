from communication import SmsSender, MailSender


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
