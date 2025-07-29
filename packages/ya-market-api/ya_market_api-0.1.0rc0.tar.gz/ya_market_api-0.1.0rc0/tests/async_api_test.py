from ya_market_api.async_api import AsyncAPI
from ya_market_api.const import Header
from ya_market_api.guide.async_api import AsyncGuideAPI
from ya_market_api.feedback.async_api import AsyncFeedbackAPI

from unittest.mock import patch

import pytest
from aiohttp.client import ClientSession


class TestAsyncAPI:
	@pytest.mark.asyncio()
	async def test___init__(self):
		session = ClientSession()
		api = AsyncAPI(session)
		assert api.session is session
		assert isinstance(api.guide, AsyncGuideAPI)
		assert isinstance(api.feedback, AsyncFeedbackAPI)
		assert api.feedback._business_id is None

		api = AsyncAPI(session, business_id=0)
		assert api.feedback._business_id == 0

	@pytest.mark.asyncio()
	async def test_build(self):
		with patch.object(AsyncAPI, "make_session") as make_session_mock:
			make_session_mock.return_value = "SESSION"
			api = await AsyncAPI.build("API_KEY")
			assert isinstance(api, AsyncAPI)
			assert api.session == "SESSION"
			assert api.feedback._business_id is None
			make_session_mock.assert_called_once_with("API_KEY")

			api = await AsyncAPI.build("API_KEY", business_id=0)
			assert api.feedback._business_id == 0

	@pytest.mark.asyncio()
	async def test_make_session(self):
		session = await AsyncAPI.make_session("API_KEY")
		assert isinstance(session, ClientSession)
		assert session.headers == {Header.API_KEY.value: "API_KEY"}
