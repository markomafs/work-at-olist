from .models import Call, Billing, BillingRule
from datetime import datetime, time, timedelta
import logging
import copy

logger = logging.getLogger(__name__)


class BillingService:
    """
    Service Responsible of handle business issues 
    between models or models and views 
    """

    def __init__(self):
        # Billing grouped by rule id
        self.billings = {}

    def create_billings(self, call=Call):
        available_rules = BillingRule.get_active_rules()

        self._split_billings_for_call(
            call=copy.copy(call),
            rules=available_rules,
        )
        for billing in self.billings.values():
            billing.calculate()
            billing.save()
        return self.billings

    def _split_billings_for_call(self, call, rules):
        for rule in rules:
            rule_start, rule_end = self._build_datetime_for_rule(
                call.started_at, rule)

            if self._time_is_matching(
                    call_start=call.started_at,
                    call_end=call.ended_at,
                    rule_start=rule_start,
                    rule_end=rule_end,
            ):

                if rule.id in self.billings:
                    billing = self.billings[rule.id]
                else:
                    billing = Billing(seconds=0)
                    self.billings[rule.id] = billing
                    billing.fk_billing_rule = rule

                billing_end = min([call.ended_at, rule_end])
                delta = billing_end - call.started_at
                billing.seconds += delta.seconds

                call.started_at = call.started_at.replace(
                    year=billing_end.year, month=billing_end.month,
                    day=billing_end.day, hour=billing_end.hour,
                    minute=billing_end.minute, second=billing_end.second,
                ) + timedelta(seconds=1)  # to reach next rule

                logger.debug('Billing Rule Applied', extra={
                    'rule': rule.id,
                    'call': call.id,
                    'delta_time': delta
                })

        if call.started_at < call.ended_at:
            self._split_billings_for_call(call=call, rules=rules)

    @staticmethod
    def _build_datetime_for_rule(
            current: datetime, rule: BillingRule) -> (datetime, datetime):

        rule_end = datetime.combine(current.date(), rule.time_end)
        rule_start = datetime.combine(current.date(), rule.time_start)

        if rule.time_end < rule.time_start:
            rule_end += timedelta(days=1)

        return rule_start, rule_end

    @staticmethod
    def _time_is_matching(call_start, call_end, rule_start, rule_end):
        is_matching = False

        is_matching |= rule_start <= call_start <= rule_end

        return is_matching
