from wb_api.base.router import Router
from wb_api.generic.functools import cache
from wb_api.const import BaseURL


class CommonRouter(Router):
	@cache
	def ping(self):
		return f"{BaseURL.COMMON.value}/ping"
