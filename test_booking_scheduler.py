import pytest
from pytest_mock import MockerFixture as mocker

from datetime import datetime
from schedule import Customer, Schedule
from communication import SmsSender, MailSender
from booking_scheduler import BookingScheduler

def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(mocker):
    scheduler = BookingScheduler(3)
    time = datetime.strptime('2025-08-01 00:01', '%Y-%m-%d %H:%M')
    customer = Customer('a', '1', 'a')
    with pytest.raises(ValueError):
        scheduler.add_schedule(Schedule(time, 1, customer))

def test_예약은_정시에만_가능하다_정시인_경우_예약가능():
    scheduler = BookingScheduler(3)
    time = datetime.strptime('2025-08-01 00:00', '%Y-%m-%d %H:%M')
    customer = Customer('a', '1', 'a')

    scheduler.add_schedule(Schedule(time, 1, customer))
    assert len(scheduler.schedules) == 1

def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생():
    pass

def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공():
    pass

def test_예약완료시_SMS는_무조건_발송():
    pass

def test_이메일이_없는_경우에는_이메일_미발송():
    pass

def test_이메일이_있는_경우에는_이메일_발송():
    pass

def test_현재날짜가_일요일인_경우_예약불가_예외처리():
    pass

def test_현재날짜가_일요일이_아닌경우_예약가능():
    pass