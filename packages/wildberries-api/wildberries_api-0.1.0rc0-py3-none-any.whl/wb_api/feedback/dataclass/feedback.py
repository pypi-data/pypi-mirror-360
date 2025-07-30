from wb_api.feedback.const import FeedbackState, FeedbackAnswerState, MatchingSize

from typing import Optional, List

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.functional_validators import field_validator
from pydantic.config import ConfigDict
from arrow import Arrow, get as get_arrow


class Answer(BaseModel):
	text: str
	state: FeedbackAnswerState
	editable: bool


class ProductDetails(BaseModel):
	imt_id: int = Field(validation_alias="imtId")
	nm_id: int = Field(validation_alias="nmId")
	product_name: str = Field(validation_alias="productName")
	supplier_article: Optional[str] = Field(validation_alias="supplierArticle")
	supplier_name: Optional[str] = Field(validation_alias="supplierName")
	brand_name: Optional[str] = Field(validation_alias="brandName")
	size: str


class PhotoLink(BaseModel):
	full_size: str = Field(validation_alias="fullSize")
	mini_size: str = Field(validation_alias="miniSize")


class Video(BaseModel):
	preview_image: str = Field(validation_alias="previewImage")
	link: str
	duration_sec: int = Field(validation_alias="durationSec")


class Feedback(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	id: str
	text: str
	pros: str
	cons: str
	product_valuation: int = Field(validation_alias="productValuation")
	created_at: Arrow = Field(validation_alias="createdDate")
	answer: Optional[Answer]
	state: FeedbackState
	product_details: ProductDetails = Field(validation_alias="productDetails")
	photo_links: Optional[List[PhotoLink]] = Field(validation_alias="photoLinks")
	video: Optional[Video]
	was_viewed: bool = Field(validation_alias="wasViewed")
	user_name: str = Field(validation_alias="userName")
	matching_size: MatchingSize = Field(validation_alias="matchingSize")
	is_able_supplier_feedback_valuation: bool = Field(validation_alias="isAbleSupplierFeedbackValuation")
	supplier_feedback_valuation: int = Field(validation_alias="supplierFeedbackValuation")
	is_able_return_product_orders: bool = Field(validation_alias="isAbleReturnProductOrders")
	return_product_orders_date: Optional[Arrow] = Field(validation_alias="returnProductOrdersDate")
	bables: Optional[List[str]]
	last_order_shk_id: int = Field(validation_alias="lastOrderShkId")
	last_order_created_at: Arrow = Field(validation_alias="lastOrderCreatedAt")
	color: str
	subject_id: int = Field(validation_alias="subjectId")
	subject_name: str = Field(validation_alias="subjectName")
	parent_feedback_id: Optional[str] = Field(validation_alias="parentFeedbackId")
	child_feedback_id: Optional[str] = Field(validation_alias="childFeedbackId")

	@field_validator("created_at", mode="before")
	@classmethod
	def dates_must_be_arrow(cls, value: str) -> Arrow:
		return get_arrow(value)

	@field_validator("return_product_orders_date", "last_order_created_at", mode="before")
	@classmethod
	def optional_dates_must_be_optional_arrow(cls, value: Optional[str]) -> Optional[Arrow]:
		if not value:
			return None

		return get_arrow(value)
