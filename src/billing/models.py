from django.db import models
import logging

logger = logging.getLogger(__name__)


class PhoneNumber(models.Model):
    area_code = models.CharField(max_length=2)
    phone_number = models.CharField(max_length=9)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone_number

    class Meta:
        unique_together = ('area_code', 'phone_number',)


class Call(models.Model):
    fk_origin_phone_number = models.ForeignKey(PhoneNumber,
                                               on_delete=models.PROTECT,
                                               related_name='origin')
    fk_destination_phone_number = models.ForeignKey(PhoneNumber,
                                                    on_delete=models.PROTECT,
                                                    related_name='destination')
    call_code = models.CharField(max_length=200)
    started_at = models.DateTimeField('call started')
    ended_at = models.DateTimeField('call ended')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.call_code


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
        logger.debug('Fetched Billing Rules', extra=active_rules.values())

        return active_rules


class Billing(models.Model):
    fk_call = models.ForeignKey(Call, on_delete=models.PROTECT)
    fk_billing_rule = models.ForeignKey(BillingRule, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    hours = models.IntegerField()
    minutes = models.IntegerField()
    seconds = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('fk_call', 'fk_billing_rule',)

    @staticmethod
    def is_hour_between(start, end, check_time):
        is_between = False

        is_between |= start <= check_time <= end
        is_between |= end < start and \
            (start <= check_time or check_time <= end)

        return is_between
