from wb_api.generic.requests.auth import JWTTokenAuth
from wb_api.common.sync_api import SyncCommonAPI
from wb_api.feedback.sync_api import SyncFeedbackAPI
from wb_api.const import Header

from requests.sessions import Session


class SyncAPI:
	session: Session
	common: SyncCommonAPI
	feedback: SyncFeedbackAPI

	def __init__(self, session: Session) -> None:
		self.session = session
		self.common = SyncCommonAPI(session)
		self.feedback = SyncFeedbackAPI(session)

	@classmethod
	def build(cls, token: str) -> "SyncAPI":
		session = cls.make_session(token)
		return cls(session)

	@staticmethod
	def make_session(token: str) -> Session:
		session = Session()
		session.auth = JWTTokenAuth(token, Header.AUTHORIZATION.value)

		return session
