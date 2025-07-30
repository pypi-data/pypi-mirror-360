from wb_api.base.dataclass import BaseRequest, BaseResponse
from wb_api.feedback.dataclass.feedback import Feedback


class Request(BaseRequest):
	id: str


class Response(BaseResponse):
	data: Feedback
