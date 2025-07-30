from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient

from spryx_billin.types.billing import (
    Currency,
    PaymentProvider,
    PlanStatus,
    RecurringInterval,
)


class Plans:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def create(
        self,
        name: str,
        code: str,
        price_cents: int,
        recurring_interval: RecurringInterval,
        payment_provider: PaymentProvider,
        description: str = NOT_GIVEN,
        credits: int = 0,
        currency: Currency = Currency.BRL,
        recurring_interval_count: int = 1,
        features: list = None,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Create a new plan."""
        payload = {
            "name": name,
            "code": code,
            "price_cents": price_cents,
            "recurring_interval": recurring_interval.value,
            "payment_provider": payment_provider.value,
            "credits": credits,
            "currency": currency.value,
            "recurring_interval_count": recurring_interval_count,
        }
        
        if is_given(description):
            payload["description"] = description
        if features:
            payload["features"] = features

        return await self._client.post(
            f"{self._base_url}/v1/plans",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def list(
        self,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
        status: PlanStatus = NOT_GIVEN,
        code: str = NOT_GIVEN,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """List plans."""
        params = {
            "page": page,
            "limit": limit,
            "order": order,
        }
        
        if is_given(status):
            params["status"] = status.value
        if is_given(code):
            params["code"] = code

        return await self._client.get(
            f"{self._base_url}/v1/plans",
            params=params,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def get(
        self,
        plan_id: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Get a plan."""
        return await self._client.get(
            f"{self._base_url}/v1/plans/{plan_id}",
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def create_feature(
        self,
        plan_id: str,
        feature_key: str,
        int_value: int = NOT_GIVEN,
        bool_value: bool = NOT_GIVEN,
        text_value: str = NOT_GIVEN,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Create a plan feature."""
        payload = {
            "feature_key": feature_key,
        }
        
        if is_given(int_value):
            payload["int_value"] = int_value
        if is_given(bool_value):
            payload["bool_value"] = bool_value
        if is_given(text_value):
            payload["text_value"] = text_value

        return await self._client.post(
            f"{self._base_url}/v1/plans/{plan_id}/features",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def delete_feature(
        self,
        plan_id: str,
        feature_key: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Delete a plan feature."""
        return await self._client.delete(
            f"{self._base_url}/v1/plans/{plan_id}/features/{feature_key}",
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def update_status(
        self,
        plan_id: str,
        status: PlanStatus,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Update a plan status."""
        payload = {
            "status": status.value,
        }

        return await self._client.put(
            f"{self._base_url}/v1/plans/{plan_id}/status",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        ) 