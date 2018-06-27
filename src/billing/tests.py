from django.test import TestCase
from .models import PhoneNumber, BillingRule, Billing
from datetime import time


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
