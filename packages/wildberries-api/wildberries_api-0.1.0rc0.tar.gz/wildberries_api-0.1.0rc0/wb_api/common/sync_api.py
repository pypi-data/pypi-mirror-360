from wb_api.base.sync_api_mixin import SyncAPIMixin
from wb_api.common.base_api import BaseCommonAPI
from wb_api.base.dataclass import PingResponse


class SyncCommonAPI(SyncAPIMixin, BaseCommonAPI):
	def ping(self) -> PingResponse:
		url = self.router.ping()
		response = self.session.get(url)
		self.validate_response(response)
		return PingResponse.model_validate_json(response.text)
