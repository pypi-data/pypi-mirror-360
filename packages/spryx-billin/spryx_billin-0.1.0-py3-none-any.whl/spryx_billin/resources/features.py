from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient

from spryx_billin.types.billing import FeatureType


class Features:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def create(
        self,
        feature_type: FeatureType,
        name: str,
        description: str,
        feature_key: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Create a new feature definition."""
        payload = {
            "type": feature_type.value,
            "name": name,
            "description": description,
            "feature_key": feature_key,
        }

        return await self._client.post(
            f"{self._base_url}/v1/features",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        )

    async def list(
        self,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
        feature_type: FeatureType = NOT_GIVEN,
    ) -> dict:
        """List all features."""
        params = {
            "page": page,
            "limit": limit,
            "order": order,
        }
        
        if is_given(feature_type):
            params["type"] = feature_type.value

        return await self._client.get(
            f"{self._base_url}/v1/features",
            params=params,
        )

    async def retrieve(
        self,
        feature_key: str,
    ) -> dict:
        """Retrieve a feature definition by its key."""
        return await self._client.get(
            f"{self._base_url}/v1/features/{feature_key}",
        )

    async def delete(
        self,
        feature_key: str,
    ) -> dict:
        """Delete a feature definition by its key."""
        return await self._client.delete(
            f"{self._base_url}/v1/features/{feature_key}",
        ) 