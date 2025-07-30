from typing import Literal

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.config import ConfigDict
from pydantic.functional_validators import field_validator
from arrow import Arrow, get as get_arrow


class Response(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	ts: Arrow = Field(validation_alias="TS")
	status: Literal["OK"] = Field(validation_alias="Status")

	@field_validator("ts", mode="before")
	@classmethod
	def ts_is_arrow(cls, value: str) -> Arrow:
		return get_arrow(value)
