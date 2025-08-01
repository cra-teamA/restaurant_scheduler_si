from communication import SmsSender

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
