from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient

from spryx_billin.types.billing import CreditPricingStatus


class CreditPricing:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def create(
        self,
        provider: str,
        model: str,
        resource_type: str,
        credits_per_unit: float,
        unit_size: int = 1,
        extra_data: dict = None,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Create a new credit pricing."""
        payload = {
            "provider": provider,
            "model": model,
            "resource_type": resource_type,
            "credits_per_unit": credits_per_unit,
            "unit_size": unit_size,
        }
        
        if extra_data:
            payload["extra_data"] = extra_data

        return await self._client.post(
            f"{self._base_url}/credit-pricing",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def list(
        self,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
        provider: str = NOT_GIVEN,
        model: str = NOT_GIVEN,
        resource_type: str = NOT_GIVEN,
        status: CreditPricingStatus = NOT_GIVEN,
        version: int = NOT_GIVEN,
        include_inactive: bool = False,
    ) -> dict:
        """List credit pricing."""
        params = {
            "page": page,
            "limit": limit,
            "order": order,
            "include_inactive": include_inactive,
        }
        
        if is_given(provider):
            params["provider"] = provider
        if is_given(model):
            params["model"] = model
        if is_given(resource_type):
            params["resource_type"] = resource_type
        if is_given(status):
            params["status"] = status.value
        if is_given(version):
            params["version"] = version

        return await self._client.get(
            f"{self._base_url}/credit-pricing",
            params=params,
        )

    async def retrieve(
        self,
        credit_pricing_id: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Retrieve a credit pricing by ID."""
        return await self._client.get(
            f"{self._base_url}/credit-pricing/{credit_pricing_id}",
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def update(
        self,
        credit_pricing_id: str,
        credits_per_unit: float,
        reason: str,
        unit_size: int = 1,
        extra_data: dict = None,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Update credit pricing by creating a new version."""
        payload = {
            "credits_per_unit": credits_per_unit,
            "reason": reason,
            "unit_size": unit_size,
        }
        
        if extra_data:
            payload["extra_data"] = extra_data

        return await self._client.put(
            f"{self._base_url}/credit-pricing/{credit_pricing_id}",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def deactivate(
        self,
        credit_pricing_id: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Deactivate a credit pricing by setting its status to INACTIVE."""
        return await self._client.patch(
            f"{self._base_url}/credit-pricing/{credit_pricing_id}/deactivate",
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def calculate_cost(
        self,
        provider: str,
        model: str,
        resource_type: str,
        units_consumed: int,
    ) -> dict:
        """Calculate credit cost for given provider/model/resource combination.
        
        This endpoint serves as a "calculator" to estimate credit costs
        before actually consuming credits.
        """
        payload = {
            "provider": provider,
            "model": model,
            "resource_type": resource_type,
            "units_consumed": units_consumed,
        }

        return await self._client.post(
            f"{self._base_url}/credit-pricing/calculate",
            json=payload,
        ) 