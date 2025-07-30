from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient


class OrgCustomers:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def create(
        self,
        name: str,
        email: str,
        organization_id: str = NOT_GIVEN,
    ) -> dict:
        """Create a new organization customer."""
        payload = {
            "name": name,
            "email": email,
        }

        return await self._client.post(
            f"{self._base_url}/v1/org-costumers",
            json=payload,
            headers={"x-organization-id": organization_id} if is_given(organization_id) else None,
        ) 