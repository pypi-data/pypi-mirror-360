from wb_api.base.dataclass import BaseResponse

from pydantic.main import BaseModel
from pydantic.fields import Field


class Data(BaseModel):
	has_new_questions: bool = Field(validation_alias="hasNewQuestions")
	has_new_feedbacks: bool = Field(validation_alias="hasNewFeedbacks")


class Response(BaseResponse):
	data: Data
