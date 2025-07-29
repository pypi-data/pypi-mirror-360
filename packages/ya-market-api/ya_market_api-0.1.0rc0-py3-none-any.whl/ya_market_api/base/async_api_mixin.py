from http import HTTPStatus

from aiohttp.client import ClientSession, ClientResponse


class AsyncAPIMixin:
	session: ClientSession

	def __init__(self, session: ClientSession, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		self.session = session

	def validate_response(self, response: ClientResponse) -> None:
		if response.status != HTTPStatus.OK:
			raise RuntimeError("Response is not valid")
