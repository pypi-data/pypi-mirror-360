from wb_api.const import Header
from wb_api.common.async_api import AsyncCommonAPI
from wb_api.feedback.async_api import AsyncFeedbackAPI

from aiohttp.client import ClientSession


class AsyncAPI:
	session: ClientSession
	common: AsyncCommonAPI
	feedback: AsyncFeedbackAPI

	def __init__(self, session: ClientSession) -> None:
		self.session = session
		self.common = AsyncCommonAPI(session)
		self.feedback = AsyncFeedbackAPI(session)

	@classmethod
	async def build(cls, token: str) -> "AsyncAPI":
		session = await cls.make_session(token)

		return cls(session)

	@staticmethod
	async def make_session(token: str) -> ClientSession:
		session = ClientSession(headers={Header.AUTHORIZATION.value: token})
		return session
