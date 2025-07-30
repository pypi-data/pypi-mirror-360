from wb_api.base.dataclass import BaseRequest, BaseResponse
from wb_api.feedback.dataclass.question import Question

from typing import Optional, Literal, List

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.functional_validators import model_validator
from pydantic.functional_serializers import field_serializer
from pydantic.config import ConfigDict
from arrow import Arrow


class Request(BaseRequest):
	model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

	is_answered: bool = Field(serialization_alias="isAnswered")
	take: int = Field(ge=1, le=10_000)
	skip: int = Field(ge=0, le=10_000)
	nm_id: Optional[int] = Field(default=None, serialization_alias="nmId")
	order: Optional[Literal["dateAsc", "dateDesc"]] = None
	date_from: Optional[Arrow] = Field(default=None, serialization_alias="dateFrom")
	date_to: Optional[Arrow] = Field(default=None, serialization_alias="dateTo")

	@field_serializer("date_from", "date_to", mode="plain")
	def optional_dates_must_be_int(self, value: Optional[Arrow]) -> Optional[int]:
		if value is None:
			return None

		return value.int_timestamp

	@field_serializer("is_answered", mode="plain")
	def optional_bool_must_be_str(self, value: Optional[bool]) -> Optional[str]:
		if value is None:
			return None

		return "true" if value else "false"

	@model_validator(mode="after")
	def verify_pagination(self):
		if self.take + self.skip > 10_000:
			raise ValueError("Sum of take and skip cannot be greater than 10000")

		return self


class Data(BaseModel):
	count_unanswered: int = Field(validation_alias="countUnanswered")
	count_archive: int = Field(validation_alias="countArchive")
	questions: List[Question]


class Response(BaseResponse):
	data: Data
