from wb_api.base.dataclass import BaseRequest

from pydantic.fields import Field


class Request(BaseRequest):
	id: str
	supplier_feedback_valuation: int = Field(serialization_alias="supplierFeedbackValuation")
