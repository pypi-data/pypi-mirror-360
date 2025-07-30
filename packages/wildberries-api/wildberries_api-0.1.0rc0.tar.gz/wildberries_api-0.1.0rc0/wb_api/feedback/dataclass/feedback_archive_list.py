from wb_api.base.dataclass import BaseRequest, BaseResponse
from wb_api.feedback.dataclass.feedback import Feedback

from typing import List, Optional, Literal

from pydantic.main import BaseModel
from pydantic.fields import Field


class Request(BaseRequest):
	take: int
	skip: int

	nm_id: Optional[int] = Field(default=None, serialization_alias="nmId")
	order: Optional[Literal["dateAsc", "dateDesc"]] = None


class Data(BaseModel):
	feedbacks: List[Feedback]


class Response(BaseResponse):
	data: Data
