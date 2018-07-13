from django.db import models
from datetime import datetime, date, timedelta
from django.db.models import Sum

import logging

logger = logging.getLogger(__name__)


class PhoneNumber(models.Model):
    MIN_PHONE = 1000000000
    MAX_PHONE = 99999999999
    phone_number = models.CharField(max_length=11, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.phone_number)

    @staticmethod
    def get_instance(phone_number):
        phone_number = str(phone_number)
        phone_model, created = PhoneNumber.objects.get_or_create(
            phone_number=phone_number,
        )
        if created is True:
            logger.debug('Created Phone Number', extra={
                'id': phone_model.id,
                'phone_number': phone_number,
            })
        return phone_model


class Call(models.Model):
    TYPE_START = 'start'
    TYPE_END = 'end'
    TYPE_CHOICES = (
        TYPE_START,
        TYPE_END
    )

    fk_origin_phone_number = models.ForeignKey(PhoneNumber,
                                               on_delete=models.PROTECT,
                                               related_name='origin')
    fk_destination_phone_number = models.ForeignKey(PhoneNumber,
                                                    on_delete=models.PROTECT,
                                                    related_name='destination')
    call_code = models.CharField(max_length=200)
    started_at = models.DateTimeField('call started')
    ended_at = models.DateTimeField('call ended', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.call_code

    # Creating On The Fly Attributes (to adapt to call request payload)
    def _get_type(self):
        """
        type field created only for Request and Response purpose
        """
        return self.TYPE_START if self.ended_at is None else self.TYPE_END

    def _set_type(self, type_name):
        pass

    type = property(_get_type, _set_type)

    def _get_timestamp(self):
        """
        timestamp field created only for Request and Response purpose
        """
        return self.started_at if self.ended_at is None else self.ended_at

    def _set_timestamp(self, timestamp):
        self.created_at = timestamp

    timestamp = property(_get_timestamp, _set_timestamp)


class BillingRule(models.Model):
    time_start = models.TimeField()
    time_end = models.TimeField()
    fixed_charge = models.DecimalField(max_digits=10, decimal_places=2)
    by_minute_charge = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active', ]),
            models.Index(fields=['time_start', ]),
        ]

    @staticmethod
    def get_active_rules():
        """ This method returns all billing rules with is_active equals True
        """
        active_rules = BillingRule.objects.filter(is_active=True)

        for rule in active_rules.values():
            logger.debug('Fetched Billing Rule', extra={
                'id': rule['id'],
                'start': str(rule['time_start']),
                'end': str(rule['time_end']),
            })

        return active_rules


class Billing(models.Model):
    fk_call = models.ForeignKey(Call, on_delete=models.PROTECT)
    fk_billing_rule = models.ForeignKey(BillingRule, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    hours = models.IntegerField()
    minutes = models.IntegerField()
    seconds = models.IntegerField()
    year = models.IntegerField(default=None)
    month = models.IntegerField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = [
            ["year", "month"],
        ]
        unique_together = ('fk_call', 'fk_billing_rule',)

    def calculate(self, fixed_charge=0.0):
        billing_minutes = self.calculate_time(seconds=self.seconds)
        charge = float(self.fk_billing_rule.by_minute_charge)
        cost = (charge * billing_minutes) + fixed_charge
        self.amount = cost
        self.setup_date(self.fk_call.ended_at)

    def calculate_time(self, seconds: int) -> int:
        billing_minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(billing_minutes, 60)
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        return billing_minutes

    def setup_date(self, billing_date: datetime):
        self.year = billing_date.year
        self.month = billing_date.month

    @staticmethod
    def get_valid_report_date(year, month):
        valid_date = date.today().replace(day=1) - timedelta(days=1)
        month = int(month)
        year = int(year)
        if date(year=year, month=month, day=1) > valid_date:
            logger.exception('Invalid Report Date', extra={
                'month': month,
                'year': year,
            })
            raise Exception('Invalid Report Date')
        return year, month

    @staticmethod
    def summarized_query_set(origin_id, year, month):
        summarized_qs = Billing.objects.all().select_related(
            'fk_call__fk_origin_phone_number'
        ).values(
            'fk_call__fk_origin_phone_number__phone_number',
        ).annotate(
            Sum('amount'),
            Sum('hours'),
            Sum('minutes'),
            Sum('seconds'),
        )
        summarized = Billing._apply_report_filter(
            qs=summarized_qs, origin_id=origin_id, year=year, month=month)
        return summarized

    @staticmethod
    def _apply_report_filter(qs, origin_id, year, month):
        return qs.filter(
            fk_call__fk_origin_phone_number_id=origin_id,
            year__exact=year,
            month__exact=month,
        )

    @staticmethod
    def detailed_query_set(origin_id, year, month):
        detailed_qs = Billing.objects.all().select_related(
            'fk_call__fk_origin_phone_number'
        ).values(
            'fk_call__fk_origin_phone_number__phone_number',
            'fk_call__fk_destination_phone_number__phone_number',
            'fk_call__started_at',
            'fk_call__ended_at',
        ).annotate(
            Sum('amount'),
            Sum('hours'),
            Sum('minutes'),
            Sum('seconds'),
        )
        detailed = Billing._apply_report_filter(
            qs=detailed_qs, origin_id=origin_id, year=year, month=month)
        return detailed
