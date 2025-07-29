from ya_market_api.base.api import API
from ya_market_api.guide.router import GuideRouter


class BaseGuideAPI(API[GuideRouter]):
	@staticmethod
	def make_router():
		return GuideRouter()
