from django.test import TestCase
from .models import PhoneNumber


class PhoneNumberModelTests(TestCase):
    def test_phone_number_instance(self):
        call = PhoneNumber()
        self.assertIsInstance(call, PhoneNumber)
