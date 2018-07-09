from django.test import TestCase
from .models import PhoneNumber, BillingRule, Billing, Call
from .serializers import CallSerializer
from .services import BillingService
from datetime import time, datetime
import pytest
import uuid
import random


class PhoneNumberModelTests(TestCase):
    def test_phone_number_instance(self):
        call = PhoneNumber()
        self.assertIsInstance(call, PhoneNumber)

    @staticmethod
    def create_number():
        phone = random.randint(PhoneNumber.MIN_PHONE, PhoneNumber.MAX_PHONE)
        return str(phone)


class BillingRuleModelTests(TestCase):

    def setUp(self):
        BillingRule.objects.create(
            id=1,
            time_start=time(6, 0, 0),
            time_end=time(22, 0, 0),
            fixed_charge=0.36,
            by_minute_charge=0.09,
            is_active=True,
        )
        BillingRule.objects.create(
            id=2,
            time_start=time(22, 0, 0),
            time_end=time(6, 0, 0),
            fixed_charge=0.36,
            by_minute_charge=0.0,
            is_active=True,
        )
        BillingRule.objects.create(
            id=3,
            time_start=time(6, 0, 0),
            time_end=time(8, 0, 0),
            fixed_charge=0.1,
            by_minute_charge=0.0,
            is_active=False,
        )

    def tearDown(self):
        BillingRule.objects.filter(id__in=[1, 2, 3, ]).delete()

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


class BillingModelTests(TestCase):
    def test_hours_between(self):
        self.assertTrue(
            Billing.is_hour_between(
                start=time(6, 0, 0),
                end=time(8, 0, 0),
                check_time=time(7, 0, 0)
            )
        )

        self.assertTrue(
            Billing.is_hour_between(
                start=time(22, 0, 0),
                end=time(8, 0, 0),
                check_time=time(2, 0, 0)
            )
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

    @staticmethod
    def create_data(
            call_id, origin=None, destination=None,
            call_code=None, timestamp=None
    ):
        if origin is None:
            origin = PhoneNumberModelTests.create_number()

        if destination is None:
            destination = PhoneNumberModelTests.create_number()

        if call_code is None:
            # see https://docs.python.org/3.6/library/uuid.html
            call_code = str(uuid.uuid4())

        if timestamp is None:
            timestamp = datetime.now()

        data = {
            'id': call_id,
            'call_code': call_code,
            'origin': origin,
            'destination': destination,
            'type': Call.TYPE_START,
            'timestamp': timestamp,
        }
        return data

    @staticmethod
    def update_data(call_id, call_code=None, timestamp=None):
        if call_code is None:
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
    "call_start, call_end, billing_rules, expected_rule_ids",
    [
        (
            datetime(2018, 7, 8, 23, 20, 10), datetime(2018, 7, 9, 3, 20, 10),
            rules, [rule_one]
        ),
    ]
)
def test_simples_billings_on_call(
        call_start, call_end, billing_rules, expected_rule_ids):
    call = Call(started_at=call_start, ended_at=call_end)
    service = BillingService()
    rules_dict = service.get_billings_on_call(
        call=call, billing_rules=billing_rules)
    assert set(rules_dict.keys()) == set(expected_rule_ids)
