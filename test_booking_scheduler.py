import pytest
import pytest_mock
from datetime import datetime, timedelta
from schedule import Customer, Schedule
from communication import SmsSender, MailSender
from booking_scheduler import BookingScheduler

UNDER_CAPACITY = 1
CAPACITY_PER_HOUR = 3
ON_THE_HOUR = datetime.strptime('2025-08-01 00:00', '%Y-%m-%d %H:%M')
NOT_ON_THE_HOUR = datetime.strptime('2025-08-01 00:01', '%Y-%m-%d %H:%M')

SUNDAY = datetime.strptime('2025-08-03 00:00', '%Y-%m-%d %H:%M')
MONDAY = datetime.strptime('2025-08-04 00:00', '%Y-%m-%d %H:%M')

@pytest.fixture
def booking_scheduler():
    return BookingScheduler(CAPACITY_PER_HOUR)


@pytest.fixture
def booking_scheduler_with_mock_sender(mocker):
    scheduler = BookingScheduler(CAPACITY_PER_HOUR)
    sms_sender = mocker.Mock()
    mail_sender = mocker.Mock()
    scheduler.set_sms_sender(sms_sender)
    scheduler.set_mail_sender(mail_sender)
    return scheduler, sms_sender, mail_sender


@pytest.fixture
def customer(mocker):
    customer = mocker.Mock()
    customer.get_email.return_value = None
    return customer


@pytest.fixture
def customer_with_email(mocker):
    customer = mocker.Mock()
    customer.get_email.return_value = 'abc@email.com'
    return customer


def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(booking_scheduler, customer):
    schedule = Schedule(NOT_ON_THE_HOUR, UNDER_CAPACITY, customer)
    with pytest.raises(ValueError):
        booking_scheduler.add_schedule(schedule)


def test_예약은_정시에만_가능하다_정시인_경우_예약가능(booking_scheduler, customer):
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, customer)
    booking_scheduler.add_schedule(schedule)
    assert booking_scheduler.has_schedule(schedule)


def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생(booking_scheduler, customer):
    schedule = Schedule(ON_THE_HOUR, CAPACITY_PER_HOUR, customer)
    booking_scheduler.add_schedule(schedule)
    schedule = Schedule(ON_THE_HOUR, 1, customer)
    with pytest.raises(ValueError):
        booking_scheduler.add_schedule(schedule)


def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공(booking_scheduler, customer):
    schedule = Schedule(ON_THE_HOUR, CAPACITY_PER_HOUR, customer)
    booking_scheduler.add_schedule(schedule)
    different_time = ON_THE_HOUR + timedelta(hours=1)
    new_schedule = Schedule(different_time, 1, customer)
    booking_scheduler.add_schedule(new_schedule)

    assert booking_scheduler.has_schedule(schedule)
    assert booking_scheduler.has_schedule(schedule)


def test_예약완료시_SMS는_무조건_발송(mocker, booking_scheduler, customer):
    orig_sender = booking_scheduler.sms_sender
    mock_sender = mocker.Mock(spec=SmsSender)
    booking_scheduler.set_sms_sender(mock_sender)
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, customer)
    booking_scheduler.add_schedule(schedule)
    booking_scheduler.set_sms_sender(orig_sender)
    assert mock_sender.send.call_count == 1


def test_예약완료시_SMS는_무조건_발송2(booking_scheduler_with_mock_sender, customer):
    booking_scheduler, sender, _ = booking_scheduler_with_mock_sender
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, customer)
    booking_scheduler.add_schedule(schedule)
    sender.send.assert_called()


def test_이메일이_없는_경우에는_이메일_미발송(booking_scheduler_with_mock_sender, customer):
    booking_scheduler, _, sender = booking_scheduler_with_mock_sender
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, customer)
    booking_scheduler.add_schedule(schedule)
    sender.send_mail.assert_not_called()


def test_이메일이_있는_경우에는_이메일_발송(booking_scheduler_with_mock_sender, customer_with_email):
    booking_scheduler, _, sender = booking_scheduler_with_mock_sender
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, customer_with_email)
    booking_scheduler.add_schedule(schedule)
    sender.send_mail.assert_called()


def test_현재날짜가_일요일인_경우_예약불가_예외처리(mocker, customer):
    mock_get_now = mocker.patch(
        'booking_scheduler.BookingScheduler.get_now',
        return_value = SUNDAY
    )
    booking_scheduler = BookingScheduler(CAPACITY_PER_HOUR)
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, customer)
    with pytest.raises(ValueError):
        booking_scheduler.add_schedule(schedule)


def test_현재날짜가_일요일이_아닌경우_예약가능(mocker, customer):
    mock_get_now = mocker.patch(
        'booking_scheduler.BookingScheduler.get_now',
        return_value = MONDAY
    )
    booking_scheduler = BookingScheduler(CAPACITY_PER_HOUR)
    schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, customer)
    booking_scheduler.add_schedule(schedule)
    assert booking_scheduler.has_schedule(schedule)
