import pytest
from pytest_mock import MockerFixture as mocker
from datetime import datetime, timedelta
from schedule import Customer, Schedule
from communication import SmsSender, MailSender
from booking_scheduler import BookingScheduler
from double import MockSmsSender, MockMailSender, MockBookingScheduler

UNDER_CAPACITY = 1
CAPACITY_PER_HOUR = 3
ON_THE_HOUR = datetime.strptime('2025-08-01 00:00', '%Y-%m-%d %H:%M')
NOT_ON_THE_HOUR = datetime.strptime('2025-08-01 00:01', '%Y-%m-%d %H:%M')
CUSTOMER = Customer('MR', '123-1234', 'abc@email.com')
CUSTOMER_WITH_NO_MAIL = Customer('MR', '123-1234', None)
@pytest.fixture
def booking_scheduler():
    return BookingScheduler(CAPACITY_PER_HOUR)

@pytest.fixture
def booking_scheduler_with_mock_sender():
    scheduler = BookingScheduler(CAPACITY_PER_HOUR)
    sms_sender = MockSmsSender()
    mail_sender = MockMailSender()
    scheduler.set_sms_sender(sms_sender)
    scheduler.set_mail_sender(mail_sender)
    return scheduler, sms_sender, mail_sender

def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(booking_scheduler):
    schedule = Schedule(NOT_ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
    with pytest.raises(ValueError):
        booking_scheduler.add_schedule(schedule)


def test_예약은_정시에만_가능하다_정시인_경우_예약가능(booking_scheduler):
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
    booking_scheduler.add_schedule(schedule)
    assert booking_scheduler.has_schedule(schedule)


def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생(booking_scheduler):
    schedule = Schedule(ON_THE_HOUR, CAPACITY_PER_HOUR, CUSTOMER)
    booking_scheduler.add_schedule(schedule)
    schedule = Schedule(ON_THE_HOUR, 1, CUSTOMER)
    with pytest.raises(ValueError):
        booking_scheduler.add_schedule(schedule)


def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공(booking_scheduler):
    schedule = Schedule(ON_THE_HOUR, CAPACITY_PER_HOUR, CUSTOMER)
    booking_scheduler.add_schedule(schedule)
    different_time = ON_THE_HOUR + timedelta(hours=1)
    new_schedule = Schedule(different_time, 1, CUSTOMER)
    booking_scheduler.add_schedule(new_schedule)

    assert booking_scheduler.has_schedule(schedule)
    assert booking_scheduler.has_schedule(schedule)


def test_예약완료시_SMS는_무조건_발송(mocker, booking_scheduler):
    orig_sender = booking_scheduler.sms_sender
    mock_sender = mocker.Mock(spec=SmsSender)
    booking_scheduler.set_sms_sender(mock_sender)
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
    booking_scheduler.add_schedule(schedule)
    booking_scheduler.set_sms_sender(orig_sender)
    assert mock_sender.send.call_count == 1

def test_예약완료시_SMS는_무조건_발송(booking_scheduler_with_mock_sender):
    booking_scheduler, sender, _ = booking_scheduler_with_mock_sender
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
    booking_scheduler.add_schedule(schedule)
    assert sender.send_called

def test_이메일이_없는_경우에는_이메일_미발송(booking_scheduler_with_mock_sender):
    booking_scheduler,  _, sender = booking_scheduler_with_mock_sender
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER_WITH_NO_MAIL)
    booking_scheduler.add_schedule(schedule)
    assert sender.send_mail_count == 0


def test_이메일이_있는_경우에는_이메일_발송(booking_scheduler_with_mock_sender):
    booking_scheduler,  _, sender = booking_scheduler_with_mock_sender
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
    booking_scheduler.add_schedule(schedule)
    assert sender.send_mail_count == 1


def test_현재날짜가_일요일인_경우_예약불가_예외처리():
    booking_scheduler = MockBookingScheduler(CAPACITY_PER_HOUR, '2025-08-03 00:00')
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
    with pytest.raises(ValueError):
        booking_scheduler.add_schedule(schedule)



def test_현재날짜가_일요일이_아닌경우_예약가능():
    booking_scheduler = MockBookingScheduler(CAPACITY_PER_HOUR, '2025-08-04 00:00')
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
    booking_scheduler.add_schedule(schedule)

    assert booking_scheduler.has_schedule(schedule)
