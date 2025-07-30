from wb_api.base.async_api_mixin import AsyncAPIMixin
from wb_api.base.dataclass import PingResponse
from wb_api.common.base_api import BaseCommonAPI


class AsyncCommonAPI(AsyncAPIMixin, BaseCommonAPI):
	async def ping(self) -> PingResponse:
		url = self.router.ping()

		async with self.session.get(url) as response:
			self.validate_response(response)
			return PingResponse.model_validate_json(await response.text())
