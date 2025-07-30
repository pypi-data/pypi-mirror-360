from wb_api.base.dataclass import BaseRequest, BaseResponse

from typing import Literal

from pydantic.main import BaseModel


class RequestAnswer(BaseModel):
	text: str


class Request(BaseRequest):
	id: str
	answer: RequestAnswer
	state: Literal["none"] = "none"

	@classmethod
	def create(cls, feedback_id: str, text: str) -> "Request":
		return cls(id=feedback_id, answer=RequestAnswer(text=text))


Response = BaseResponse
