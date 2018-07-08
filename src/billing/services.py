from .models import Call, Billing, BillingRule
import logging

logger = logging.getLogger(__name__)


class BillingService:
    """
    Service Responsible of handle business issues 
    between models or models and views 
    """

    def create_billing(self, call=Call):
        billing = Billing()
        return billing
