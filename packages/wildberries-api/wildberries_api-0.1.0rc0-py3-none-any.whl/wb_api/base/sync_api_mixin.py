from http import HTTPStatus

from requests.sessions import Session
from requests.models import Response


class SyncAPIMixin:
	session: Session

	def __init__(self, session: Session, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		self.session = session

	def validate_response(self, response: Response, expected_status: HTTPStatus = HTTPStatus.OK) -> None:
		if response.status_code != expected_status:
			raise RuntimeError("Response is not valid")
