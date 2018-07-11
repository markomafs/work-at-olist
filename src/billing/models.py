from django.db import models
import logging

logger = logging.getLogger(__name__)


class PhoneNumber(models.Model):
    MIN_PHONE = 1000000000
    MAX_PHONE = 99999999999
    area_code = models.CharField(max_length=2)
    phone_number = models.CharField(max_length=9)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.formatted()

    class Meta:
        unique_together = ('area_code', 'phone_number',)

    def formatted(self):
        formatted_number = '{area_code}{phone_number}'.format(
            phone_number=self.phone_number,
            area_code=self.area_code,
        )
        logger.debug('Phone Number Formatted', extra={
            'output': formatted_number,
            'area_code': self.area_code,
            'phone_number': self.phone_number,
        })
        return formatted_number

    @staticmethod
    def get_instance(full_number):
        full_number = str(full_number)
        area_code = full_number[:2]
        number = full_number[2:]
        phone_number, created = PhoneNumber.objects.get_or_create(
            area_code=area_code,
            phone_number=number
        )
        if created is True:
            logger.debug('Created Phone Number', extra={
                'area_code': area_code,
                'phone_number': phone_number
            })
        return phone_number


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
            logger.debug('Fetched Billing Rule', extra=rule)

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
