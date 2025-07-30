from wb_api.base.dataclass import BaseResponse

from pydantic.main import BaseModel
from pydantic.fields import Field


class Data(BaseModel):
	count_unanswered: int = Field(validation_alias="countUnanswered")
	count_unanswered_today: int = Field(validation_alias="countUnansweredToday")


class Response(BaseResponse):
	data: Data
