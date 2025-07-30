from spryx_http import SpryxAsyncClient

from spryx_billin.resources.credit_balances import CreditBalances
from spryx_billin.resources.credit_pricing import CreditPricing
from spryx_billin.resources.org_customers import OrgCustomers
from spryx_billin.resources.features import Features
from spryx_billin.resources.webhooks import Webhooks
from spryx_billin.resources.subscriptions import Subscriptions
from spryx_billin.resources.plans import Plans


class SpryxBilling(SpryxAsyncClient):
    def __init__(
        self,
        application_id: str,
        application_secret: str,
        base_url: str = "https://dev-billing.spryx.ai",
        iam_base_url: str = "https://dev-iam.spryx.ai",
    ):
        super().__init__(
            base_url=base_url,
            iam_base_url=iam_base_url,
            application_id=application_id,
            application_secret=application_secret,
        )

        self.credit_balances = CreditBalances(self)
        self.credit_pricing = CreditPricing(self)
        self.org_customers = OrgCustomers(self)
        self.features = Features(self)
        self.webhooks = Webhooks(self)
        self.subscriptions = Subscriptions(self)
        self.plans = Plans(self) 