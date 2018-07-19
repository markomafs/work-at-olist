from django.test import TestCase
from .models import PhoneNumber, BillingRule, Billing, Call
from .serializers import CallSerializer
from .services import BillingService
from datetime import time, datetime, date, timedelta
import pytest
import uuid
import random
import pytz


class PhoneNumberModelTests(TestCase):
    def test_phone_number_instance(self):
        str_number = self.create_number()
        number = PhoneNumber(phone_number=str_number)
        self.assertIsInstance(number, PhoneNumber)
        self.assertEqual(str_number, number.__str__())

    @staticmethod
    def create_number():
        phone = random.randint(PhoneNumber.MIN_PHONE, PhoneNumber.MAX_PHONE)
        return str(phone)


class BillingRuleModelTests(TestCase):
    def setUp(self):
        # id 1 and 2 was created By Migrations
        BillingRule.objects.create(
            id=3,
            time_start=time(6, 0, 0),
            time_end=time(8, 0, 0),
            fixed_charge=0.1,
            by_minute_charge=0.0,
            is_active=False,
        )

    def tearDown(self):
        BillingRule.objects.get(id=3).delete()

    def test_active_billing_rules(self):
        """ this should test get_active_rules from BillingRule Class
            expected 2 rules based on Setup function
        """
        available_rules = BillingRule.get_active_rules()

        self.assertEqual(
            len(available_rules), 2,
            msg='Should Retrieve 2 rules'
        )

    @staticmethod
    def create_rule(
            rule_id, time_start=None, time_end=None, fixed_charge=0,
            by_minute_charge=0, is_active=True
    ):
        return BillingRule(
            id=rule_id,
            time_start=time_start,
            time_end=time_end,
            fixed_charge=fixed_charge,
            by_minute_charge=by_minute_charge,
            is_active=is_active,
        )


# class CallModelTest(TestCase):
default_start = datetime(2018, 6, 8)
default_end = datetime(2018, 6, 9)


@pytest.mark.parametrize("started, ended, expected", [
    (default_start, None, default_start),
    (default_start, default_end, default_end),
    (None, None, None),
    (None, default_end, default_end),
])
def test_timestamp_property(started, ended, expected):
    call = Call(started_at=started, ended_at=ended)
    assert call.timestamp == expected


@pytest.mark.parametrize("ended, expected_type", [
    (default_end, Call.TYPE_END),
    (None, Call.TYPE_START),
])
def test_type_property(ended, expected_type):
    call = Call(ended_at=ended)
    assert call.type == expected_type


class CallSerializerTest(TestCase):
    call_id = 1

    def test_call_serializer(self):
        # Testing Creating
        create = self.create_data(self.call_id)
        serializer = CallSerializer(data=create)
        assert serializer.is_valid()
        serializer.create(serializer.data)

        # Testing Update
        call = Call.objects.get(id=self.call_id)
        update = CallSerializer(data=self.update_data(self.call_id))
        assert update.is_valid()
        update_data = dict(
            list(update.validated_data.items())
        )
        serializer.update(call, update_data)

        # Validating Success
        call = Call.objects.get(id=self.call_id)
        assert call.started_at == create['timestamp'].replace(
            tzinfo=call.started_at.tzinfo)
        assert call.ended_at == update_data['timestamp']

    def test_invalid_timestamp(self):
        # Testing Creating
        create = self.create_data(self.call_id)
        started = create["timestamp"]
        serializer = CallSerializer(data=create)
        assert serializer.is_valid()
        serializer.create(serializer.data)

        # Testing Update
        call = Call.objects.get(id=self.call_id)
        update = CallSerializer(
            data=self.update_data(
                call_id=self.call_id,
                timestamp=(started - timedelta(days=1))
            )
        )
        assert update.is_valid()
        update_data = dict(
            list(update.validated_data.items())
        )
        serializer.update(call, update_data)

    @staticmethod
    def create_data(call_id):
        source = PhoneNumberModelTests.create_number()
        destination = PhoneNumberModelTests.create_number()
        # see https://docs.python.org/3.6/library/uuid.html
        call_code = str(uuid.uuid4())
        timestamp = datetime.now()

        data = {
            'id': call_id,
            'call_code': call_code,
            'source': source,
            'destination': destination,
            'type': Call.TYPE_START,
            'timestamp': timestamp,
        }
        return data

    @staticmethod
    def update_data(call_id, timestamp=None):
        call_code = str(uuid.uuid4())
        if timestamp is None:
            timestamp = datetime.now()

        data = {
            'id': call_id,
            'call_code': call_code,
            'type': Call.TYPE_END,
            'timestamp': timestamp,
        }
        return data


rule_one = 1
rule_two = 2
rules = [
    BillingRuleModelTests.create_rule(
        rule_id=rule_one, time_start=time(22, 0, 1), time_end=time(8, 0, 0)
    ),
    BillingRuleModelTests.create_rule(
        rule_id=rule_two, time_start=time(8, 0, 1), time_end=time(22, 0, 0)
    ),
]


# class BillingServiceTest(TestCase):
@pytest.mark.parametrize(
    "call_start, call_end, billing_rules, expected_billings",
    [
        (
                datetime(2018, 7, 8, 23, 20, 10, tzinfo=pytz.UTC),
                datetime(2018, 7, 12, 3, 20, 10, tzinfo=pytz.UTC),
                rules, 2
        ),
        (
                datetime(2018, 7, 9, 9, 20, 10, tzinfo=pytz.UTC),
                datetime(2018, 7, 9, 17, 20, 10, tzinfo=pytz.UTC),
                rules, 1
        ),
        (
                datetime(2018, 7, 8, 10, 20, 10, tzinfo=pytz.UTC),
                datetime(2018, 7, 9, 3, 20, 10, tzinfo=pytz.UTC),
                rules, 2
        ),
        (
                datetime(2018, 7, 9, 9, 20, 10, tzinfo=pytz.UTC),
                datetime(2018, 7, 9, 17, 20, 10, tzinfo=pytz.UTC),
                rules, 1
        ),
    ]
)
def test_simples_billings_on_call(
        call_start, call_end, billing_rules, expected_billings):
    call = Call(started_at=call_start, ended_at=call_end)
    service = BillingService()
    service._split_billings_for_call(call=call, rules=billing_rules)
    assert len(service.billings) == expected_billings


@pytest.mark.parametrize(
    "rule_start, rule_end, call_start, expected_result",
    [
        (  # Full Call between rule start and end
                datetime(2018, 7, 8, 23, 2, 11),
                datetime(2018, 7, 9, 3, 20, 10),
                datetime(2018, 7, 8, 23, 50, 10),
                True,
        ),
        (  # Call started before rule but ends between
                datetime(2018, 7, 8, 23, 20, 12),
                datetime(2018, 7, 9, 3, 20, 10),
                datetime(2018, 7, 8, 20, 50, 10),
                False,
        ),
        (  # Call start between rule start but ends after
                datetime(2018, 7, 8, 23, 20, 13),
                datetime(2018, 7, 9, 3, 21, 10),
                datetime(2018, 7, 8, 23, 50, 10),
                True,
        ),
        (  # Call start before rule and ends after rule
                datetime(2018, 7, 8, 23, 20, 17),
                datetime(2018, 7, 9, 3, 20, 9),
                datetime(2018, 7, 8, 21, 50, 10),
                False,
        ),
        (   # Call ends before rule start
                datetime(2018, 7, 8, 23, 20, 15),
                datetime(2018, 7, 9, 3, 20, 8),
                datetime(2018, 7, 8, 20, 50, 10),
                False,
        ),
        (   # Call start after rule ends
                datetime(2018, 7, 8, 23, 20, 19),
                datetime(2018, 7, 9, 4, 20, 10),
                datetime(2018, 7, 10, 23, 50, 10),
                False,
        ),
        (  # Call start at the same time as rule start
                datetime(2018, 7, 8, 23, 20, 10),
                datetime(2018, 7, 9, 3, 20, 10),
                datetime(2018, 7, 8, 23, 20, 10),
                True,
        ),
    ]
)
def test_if_time_is_matching(
        call_start, rule_start, rule_end, expected_result):
    result = BillingService._time_is_matching(
        call_start=call_start,
        rule_start=rule_start,
        rule_end=rule_end,
    )
    assert result == expected_result


# class BillingModelTest(TestCase):
@pytest.mark.parametrize(
    "seconds, fixed, charge, ended_at, expected_amount",
    [
        (1800, 0, 0.10, datetime(2018, 7, 12, 3, 20, 10), 3.00),
        (60, 10, 0.30, datetime(2018, 7, 12, 3, 20, 10), 10.30),
        (240, 10, 0.0, datetime(2018, 7, 12, 3, 20, 10), 10.00),
        (100, 0, 0.0, datetime(2018, 7, 12, 3, 20, 10), 0.00),
    ]
)
def test_calculated_billing(seconds, fixed, charge, ended_at, expected_amount):
    call = Call(ended_at=ended_at)
    rule = BillingRule(by_minute_charge=charge)
    billing = Billing(fk_call=call, fk_billing_rule=rule, seconds=seconds)

    billing.calculate(fixed_charge=fixed)

    assert billing.amount == expected_amount

current_date = date.today()
last_month = current_date.replace(day=1) - timedelta(days=1)
next_month = current_date.replace(day=1) + timedelta(days=31)


@pytest.mark.parametrize(
    "year, month, expected_year, expected_month",
    [
        (2018, 1, 2018, 1),
        (None, None, last_month.year, last_month.month),
        (last_month.year, last_month.month, last_month.year, last_month.month),
    ]
)
def test_valid_report_date(year, month, expected_year, expected_month):
    result_year, result_month = Billing.get_valid_report_date(year, month)
    assert result_year == expected_year
    assert result_month == expected_month


@pytest.mark.parametrize(
    "year, month",
    [
        (current_date.year, current_date.month),
        (next_month.year, next_month.month),
    ]
)
def test_invalid_report_date(year, month):
    with pytest.raises(Exception):
        Billing.get_valid_report_date(year, month)
