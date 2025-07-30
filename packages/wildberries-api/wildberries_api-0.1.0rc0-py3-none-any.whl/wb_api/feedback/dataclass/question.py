from wb_api.feedback.const import QuestionState

from typing import Optional

from pydantic.main import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from pydantic.functional_validators import field_validator
from arrow import Arrow, get as get_arrow


class QuestionAnswer(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	text: str
	editable: bool
	created_at: Arrow = Field(validation_alias="createDate")

	@field_validator("created_at", mode="before")
	@classmethod
	def dates_must_be_arrow(cls, value: str) -> Arrow:
		return get_arrow(value)


class QuestionProductDetails(BaseModel):
	nm_id: int = Field(validation_alias="nmId")
	imt_id: int = Field(validation_alias="imtId")
	product_name: str = Field(validation_alias="productName")
	supplier_article: str = Field(validation_alias="supplierArticle")
	supplier_name: str = Field(validation_alias="supplierName")
	brand_name: str = Field(validation_alias="brandName")


class Question(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	id: str
	text: str
	created_at: Arrow = Field(validation_alias="createdDate")
	state: QuestionState
	answer: Optional[QuestionAnswer]
	product_details: QuestionProductDetails = Field(validation_alias="productDetails")
	was_viewed: bool = Field(validation_alias="wasViewed")
	is_warned: bool = Field(validation_alias="isWarned")

	@field_validator("created_at", mode="before")
	@classmethod
	def dates_must_be_arrow(cls, value: str) -> Arrow:
		return get_arrow(value)
