from django.test import TestCase
from .models import PhoneNumber, BillingRule, Billing, Call
from datetime import time, datetime
import pytest


class PhoneNumberModelTests(TestCase):
    def test_phone_number_instance(self):
        call = PhoneNumber()
        self.assertIsInstance(call, PhoneNumber)


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
