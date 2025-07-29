from ya_market_api.const import Header
from ya_market_api.guide.async_api import AsyncGuideAPI
from ya_market_api.feedback.async_api import AsyncFeedbackAPI

from typing import Optional

from aiohttp.client import ClientSession


class AsyncAPI:
	guide: AsyncGuideAPI
	feedback: AsyncFeedbackAPI
	session: ClientSession

	def __init__(self, session: ClientSession, *, business_id: Optional[int] = None) -> None:
		self.session = session
		self.guide = AsyncGuideAPI(session)
		self.feedback = AsyncFeedbackAPI(session, business_id)

	@classmethod
	async def build(cls, api_key: str, *, business_id: Optional[int] = None) -> "AsyncAPI":
		session = await cls.make_session(api_key)

		return cls(session, business_id=business_id)

	@staticmethod
	async def make_session(api_key: str) -> ClientSession:
		session = ClientSession(headers={Header.API_KEY.value: api_key})
		return session
