from ya_market_api.generic.functools import cache
from ya_market_api.base.router import Router
from ya_market_api.const import BASE_URL


class GuideRouter(Router):
	@cache
	def token_info(self) -> str:
		return f"{BASE_URL}/auth/token"

	@cache
	def delivery_services(self) -> str:
		return f"{BASE_URL}/delivery/services"
