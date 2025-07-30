from http import HTTPStatus

from aiohttp.client import ClientSession, ClientResponse


class AsyncAPIMixin:
	session: ClientSession

	def __init__(self, session: ClientSession, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		self.session = session

	def validate_response(self, response: ClientResponse, expected_status: HTTPStatus = HTTPStatus.OK) -> None:
		if response.status != expected_status:
			raise RuntimeError("Response is not valid")
