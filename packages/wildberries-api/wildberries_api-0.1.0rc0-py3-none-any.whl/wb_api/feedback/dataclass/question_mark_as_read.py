from wb_api.base.dataclass import BaseRequest, BaseResponse

from pydantic.fields import Field


class Request(BaseRequest):
	id: str
	was_viewed: bool = Field(serialization_alias="wasViewed")


Response = BaseResponse		# From docs: type of data is object or null, but there are no examples of objects
