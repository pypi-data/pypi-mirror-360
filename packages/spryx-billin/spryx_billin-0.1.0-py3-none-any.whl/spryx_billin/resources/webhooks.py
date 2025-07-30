from spryx_http import SpryxAsyncClient


class Webhooks:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client
        self._base_url = client.base_url

    async def stripe_webhook(
        self,
        webhook_data: dict = None,
    ) -> dict:
        """Handle Stripe webhook."""
        return await self._client.post(
            f"{self._base_url}/v1/webhooks/stripe",
            json=webhook_data,
        ) 