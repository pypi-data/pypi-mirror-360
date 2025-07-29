from ya_market_api.base.api import API
from ya_market_api.feedback.router import FeedbackRouter

from typing import Optional


class BaseFeedbackAPI(API[FeedbackRouter]):
	def __init__(self, business_id: Optional[int] = None) -> None:
		super().__init__()
		self._business_id = business_id

	@property
	def business_id(self) -> int:
		if self._business_id is None:
			raise RuntimeError("The business_id was not specified")

		return self._business_id

	@staticmethod
	def make_router() -> FeedbackRouter:
		return FeedbackRouter()
