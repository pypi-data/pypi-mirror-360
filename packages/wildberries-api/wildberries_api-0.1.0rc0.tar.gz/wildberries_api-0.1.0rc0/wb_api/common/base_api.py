from wb_api.base.api import API
from wb_api.common.router import CommonRouter


class BaseCommonAPI(API[CommonRouter]):
	@staticmethod
	def make_router():
		return CommonRouter()
