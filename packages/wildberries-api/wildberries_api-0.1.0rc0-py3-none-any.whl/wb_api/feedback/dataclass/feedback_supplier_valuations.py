from wb_api.base.dataclass import BaseRequest, BaseResponse
from wb_api.const import Header

from typing import Dict, Optional, Literal

from pydantic.main import BaseModel
from pydantic.fields import Field


class Request(BaseRequest):
	locale: Optional[Literal["ru", "en", "zh"]] = Field(default=None, serialization_alias=Header.LOCALE.value)


class Data(BaseModel):
	feedback_valuations: Dict[int, str] = Field(validation_alias="feedbackValuations")
	product_valuations: Dict[int, str] = Field(validation_alias="productValuations")


class Response(BaseResponse):
	data: Data
