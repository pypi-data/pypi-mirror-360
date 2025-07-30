from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient

from spryx_billin.types.billing import BalanceType, CreditAdjustmentType


class CreditBalances:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def list(
        self,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
        period_start: str = NOT_GIVEN,
        expected_expiry_date: str = NOT_GIVEN,
        expired_at: str = NOT_GIVEN,
        balance_type: BalanceType = NOT_GIVEN,
        active: bool = NOT_GIVEN,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """List credit balances with filtering and pagination."""
        params = {
            "page": page,
            "limit": limit,
            "order": order,
        }
        
        if is_given(period_start):
            params["period_start"] = period_start
        if is_given(expected_expiry_date):
            params["expected_expiry_date"] = expected_expiry_date
        if is_given(expired_at):
            params["expired_at"] = expired_at
        if is_given(balance_type):
            params["balance_type"] = balance_type.value
        if is_given(active):
            params["active"] = active

        return await self._client.get(
            f"{self._base_url}/credit-balances",
            params=params,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def get_usage_summary(
        self,
        credit_balance_id: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Get a complete usage summary of a credit balance with calculated usage and current balance."""
        return await self._client.get(
            f"{self._base_url}/credit-balances/{credit_balance_id}/usage/summary",
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def list_usage(
        self,
        credit_balance_id: str,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
        provider: str = NOT_GIVEN,
        model: str = NOT_GIVEN,
        resource_type: str = NOT_GIVEN,
        min_credits_consumed: float = NOT_GIVEN,
        max_credits_consumed: float = NOT_GIVEN,
        start_date: str = NOT_GIVEN,
        end_date: str = NOT_GIVEN,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """List credit usage records for a specific credit balance with pagination and filtering."""
        params = {
            "page": page,
            "limit": limit,
            "order": order,
        }
        
        if is_given(provider):
            params["provider"] = provider
        if is_given(model):
            params["model"] = model
        if is_given(resource_type):
            params["resource_type"] = resource_type
        if is_given(min_credits_consumed):
            params["min_credits_consumed"] = min_credits_consumed
        if is_given(max_credits_consumed):
            params["max_credits_consumed"] = max_credits_consumed
        if is_given(start_date):
            params["start_date"] = start_date
        if is_given(end_date):
            params["end_date"] = end_date

        return await self._client.get(
            f"{self._base_url}/credit-balances/{credit_balance_id}/usages",
            params=params,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def create_usage(
        self,
        organization_id: str,
        provider: str,
        model: str,
        resource_type: str,
        units_consumed: int,
        extra_data: dict = None,
    ) -> dict:
        """Create a new credit usage record using the active credit balance for the organization."""
        payload = {
            "organization_id": organization_id,
            "provider": provider,
            "model": model,
            "resource_type": resource_type,
            "units_consumed": units_consumed,
        }
        
        if extra_data:
            payload["extra_data"] = extra_data

        return await self._client.post(
            f"{self._base_url}/credit-balances/usages",
            json=payload,
            headers={"x-organization-id": organization_id},
        )

    async def list_adjustments(
        self,
        credit_balance_id: str,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
        adjustment_type: CreditAdjustmentType = NOT_GIVEN,
        min_credits_adjusted: float = NOT_GIVEN,
        max_credits_adjusted: float = NOT_GIVEN,
        admin_user_id: str = NOT_GIVEN,
        start_date: str = NOT_GIVEN,
        end_date: str = NOT_GIVEN,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """List credit adjustment records for a specific credit balance with pagination and filtering."""
        params = {
            "page": page,
            "limit": limit,
            "order": order,
        }
        
        if is_given(adjustment_type):
            params["adjustment_type"] = adjustment_type.value
        if is_given(min_credits_adjusted):
            params["min_credits_adjusted"] = min_credits_adjusted
        if is_given(max_credits_adjusted):
            params["max_credits_adjusted"] = max_credits_adjusted
        if is_given(admin_user_id):
            params["admin_user_id"] = admin_user_id
        if is_given(start_date):
            params["start_date"] = start_date
        if is_given(end_date):
            params["end_date"] = end_date

        return await self._client.get(
            f"{self._base_url}/credit-balances/{credit_balance_id}/adjustments",
            params=params,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def create_adjustment(
        self,
        credit_balance_id: str,
        adjustment_type: CreditAdjustmentType,
        credits_adjusted: float,
        reason: str,
        admin_user_id: str = NOT_GIVEN,
        admin_notes: str = NOT_GIVEN,
        extra_data: dict = None,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Create a credit adjustment for a specific credit balance. Requires platform admin permissions."""
        payload = {
            "adjustment_type": adjustment_type.value,
            "credits_adjusted": credits_adjusted,
            "reason": reason,
        }
        
        if is_given(admin_user_id):
            payload["admin_user_id"] = admin_user_id
        if is_given(admin_notes):
            payload["admin_notes"] = admin_notes
        if extra_data:
            payload["extra_data"] = extra_data

        return await self._client.post(
            f"{self._base_url}/credit-balances/{credit_balance_id}/adjustments",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        ) 