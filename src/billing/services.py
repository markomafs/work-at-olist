from .models import Call, Billing, BillingRule
import logging

logger = logging.getLogger(__name__)


class BillingService:
    """
    Service Responsible of handle business issues 
    between models or models and views 
    """

    def create_billings(self, call=Call):
        rules = BillingRule.get_active_rules()
        billings = self.get_billings_on_call(call=call, billing_rules=rules)
        return billings

    def get_billings_on_call(self, call, billing_rules):
        rules_dict = {}
        for rule in billing_rules:
            if self._rule_matches_call(call=call, rule=rule):
                rules_dict[rule.id] = rule
        return rules_dict

    def _rule_matches_call(self, call=Call, rule=BillingRule):
        if Billing.is_hour_between(
                start=rule.time_start,
                end=rule.time_end,
                check_time=call.started_at.time()
        ):
            return True
        return False
