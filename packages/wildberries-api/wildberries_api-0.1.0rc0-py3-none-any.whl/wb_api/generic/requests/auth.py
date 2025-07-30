from requests.auth import AuthBase
from requests.models import Request


class JWTTokenAuth(AuthBase):
	def __init__(self, token: str, header_label: str = "Authorization") -> None:
		self.token = token
		self.header_label = header_label

	def __call__(self, request: Request) -> Request:
		request.headers[self.header_label] = self.token
		return request
