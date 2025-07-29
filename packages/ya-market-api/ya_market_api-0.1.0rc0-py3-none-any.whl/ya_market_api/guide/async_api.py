from ya_market_api.base.async_api_mixin import AsyncAPIMixin
from ya_market_api.guide.base_api import BaseGuideAPI
from ya_market_api.guide.dataclass import TokenInfoResponse, DeliveryServicesResponse
from ya_market_api.guide.region.async_api import AsyncGuideRegionAPI

from aiohttp.client import ClientSession


class AsyncGuideAPI(AsyncAPIMixin, BaseGuideAPI):
	def __init__(self, session: ClientSession, *args, **kwargs) -> None:
		super().__init__(session, *args, **kwargs)
		self.region = AsyncGuideRegionAPI(session, *args, **kwargs)

	async def get_token_info(self) -> TokenInfoResponse:
		url = self.router.token_info()

		async with self.session.post(url=url, json="") as response:
			self.validate_response(response)
			return TokenInfoResponse.model_validate_json(await response.text())

	async def get_delivery_services(self) -> DeliveryServicesResponse:
		url = self.router.delivery_services()

		async with self.session.get(url=url) as response:
			self.validate_response(response)
			return DeliveryServicesResponse.model_validate_json(await response.text())
