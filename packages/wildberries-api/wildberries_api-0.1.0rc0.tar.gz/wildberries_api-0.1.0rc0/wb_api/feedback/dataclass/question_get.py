from wb_api.base.dataclass import BaseRequest, BaseResponse
from wb_api.feedback.dataclass.question import Question


class Request(BaseRequest):
	id: str


class Response(BaseResponse):
	data: Question
