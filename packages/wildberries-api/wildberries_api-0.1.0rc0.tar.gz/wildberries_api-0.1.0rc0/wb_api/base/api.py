from wb_api.base.router import Router

from abc import ABC, abstractmethod
from typing import TypeVar, Generic


RouterT = TypeVar("RouterT", bound=Router)


class API(ABC, Generic[RouterT]):
	router: RouterT

	def __init__(self) -> None:
		self.router = self.make_router()

	@staticmethod
	@abstractmethod
	def make_router() -> RouterT: ...
