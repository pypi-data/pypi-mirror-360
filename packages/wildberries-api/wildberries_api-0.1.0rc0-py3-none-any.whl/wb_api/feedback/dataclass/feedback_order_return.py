from wb_api.base.dataclass import BaseRequest, BaseResponse

from pydantic.fields import Field


class Request(BaseRequest):
	feedback_id: str = Field(serialization_alias="feedbackId")


Response = BaseResponse
