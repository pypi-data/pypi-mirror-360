from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient


class Subscriptions:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def create_checkout_session(
        self,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        subscription_id: str = NOT_GIVEN,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Create a checkout session for subscription payment."""
        payload = {
            "plan_id": plan_id,
            "success_url": success_url,
            "cancel_url": cancel_url,
        }
        
        if is_given(subscription_id):
            payload["subscription_id"] = subscription_id

        return await self._client.post(
            f"{self._base_url}/v1/subscriptions/checkout-session",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def create(
        self,
        plan_id: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Create a subscription - internal use case."""
        payload = {
            "plan_id": plan_id,
        }

        return await self._client.post(
            f"{self._base_url}/v1/subscriptions",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def get_organization_subscription(
        self,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Get organization subscription."""
        return await self._client.get(
            f"{self._base_url}/v1/subscriptions/organization",
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def admin_activate(
        self,
        subscription_id: str,
        provider_subscription_id: str,
        admin_notes: str = NOT_GIVEN,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Admin endpoint to force activation of a subscription that was contracted through Stripe.
        
        This endpoint is for administrative use only and should be used when the normal
        webhook activation process fails or needs to be manually triggered.
        
        Note: This endpoint only works for subscriptions that were created through Stripe.
        """
        payload = {
            "provider_subscription_id": provider_subscription_id,
        }
        
        if is_given(admin_notes):
            payload["admin_notes"] = admin_notes

        return await self._client.post(
            f"{self._base_url}/v1/subscriptions/{subscription_id}/activate",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        ) 