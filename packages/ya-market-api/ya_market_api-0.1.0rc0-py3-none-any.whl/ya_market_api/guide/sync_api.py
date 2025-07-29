from ya_market_api.base.sync_api_mixin import SyncAPIMixin
from ya_market_api.guide.base_api import BaseGuideAPI
from ya_market_api.guide.dataclass import TokenInfoResponse, DeliveryServicesResponse
from ya_market_api.guide.region.sync_api import SyncGuideRegionAPI

from requests import Session


class SyncGuideAPI(SyncAPIMixin, BaseGuideAPI):
	def __init__(self, session: Session, *args, **kwargs) -> None:
		super().__init__(session, *args, **kwargs)
		self.region = SyncGuideRegionAPI(session, *args, **kwargs)

	def get_token_info(self) -> TokenInfoResponse:
		url = self.router.token_info()
		response = self.session.post(url=url, json="")
		self.validate_response(response)
		return TokenInfoResponse.model_validate_json(response.text)

	def get_delivery_services(self) -> DeliveryServicesResponse:
		url = self.router.delivery_services()
		response = self.session.get(url=url)
		self.validate_response(response)
		return DeliveryServicesResponse.model_validate_json(response.text)
