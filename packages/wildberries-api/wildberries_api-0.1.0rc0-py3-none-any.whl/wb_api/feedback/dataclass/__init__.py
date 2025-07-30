from wb_api.feedback.dataclass.new_feedbacks_questions import Response as NewFeedbacksQuestionsResponse
from wb_api.feedback.dataclass.question_count_unanswered import Response as QuestionCountUnansweredResponse
from wb_api.feedback.dataclass.question_count import Request as QuestionCountRequest, Response as QuestionCountResponse
from wb_api.feedback.dataclass.question_list import Request as QuestionListRequest, Response as QuestionListResponse
from wb_api.feedback.dataclass.question_mark_as_read import (
	Request as QuestionMarkAsReadRequest, Response as QuestionMarkAsReadResponse,
)
from wb_api.feedback.dataclass.question_reject import (
	Request as QuestionRejectRequest, Response as QuestionRejectResponse,
)
from wb_api.feedback.dataclass.question_answer_add import (
	Request as QuestionAnswerAddRequest, Response as QuestionAnswerAddResponse,
)
from wb_api.feedback.dataclass.question_answer_update import (
	Request as QuestionAnswerUpdateRequest, Response as QuestionAnswerUpdateResponse,
)
from wb_api.feedback.dataclass.question_get import Request as QuestionGetRequest, Response as QuestionGetResponse
from wb_api.feedback.dataclass.feedback_count_unanswered import Response as FeedbackCountUnansweredResponse
from wb_api.feedback.dataclass.feedback_count import Request as FeedbackCountRequest, Response as FeedbackCountResponse
from wb_api.feedback.dataclass.feedback_list import Request as FeedbackListRequest, Response as FeedbackListResponse
from wb_api.feedback.dataclass.feedback_supplier_valuations import (
	Request as FeedbackSupplierValuationsRequest, Response as FeedbackSupplierValuationsResponse,
)
from wb_api.feedback.dataclass.feedback_text_report import Request as FeedbackTextReportRequest
from wb_api.feedback.dataclass.feedback_product_report import Request as FeedbackProductReportRequest
from wb_api.feedback.dataclass.feedback_answer_add import Request as FeedbackAnswerAddRequest
from wb_api.feedback.dataclass.feedback_answer_update import Request as FeedbackAnswerUpdateRequest
from wb_api.feedback.dataclass.feedback_order_return import (
	Request as FeedbackOrderReturnRequest, Response as FeedbackOrderReturnResponse,
)
from wb_api.feedback.dataclass.feedback_get import Request as FeedbackGetRequest, Response as FeedbackGetResponse
from wb_api.feedback.dataclass.feedback_archive_list import Request as FeedbackArchiveListRequest, Response as FeedbackArchiveListResponse


__all__ = [
	"NewFeedbacksQuestionsResponse", "QuestionCountUnansweredResponse", "QuestionCountRequest", "QuestionCountResponse",
	"QuestionListRequest", "QuestionListResponse", "QuestionMarkAsReadRequest", "QuestionMarkAsReadResponse",
	"QuestionRejectRequest", "QuestionRejectResponse", "QuestionAnswerAddRequest", "QuestionAnswerAddResponse",
	"QuestionAnswerUpdateRequest", "QuestionAnswerUpdateResponse", "QuestionGetRequest", "QuestionGetResponse",
	"FeedbackCountUnansweredResponse", "FeedbackCountRequest", "FeedbackCountResponse", "FeedbackListRequest",
	"FeedbackListResponse", "FeedbackSupplierValuationsRequest", "FeedbackSupplierValuationsResponse",
	"FeedbackTextReportRequest", "FeedbackProductReportRequest", "FeedbackAnswerAddRequest",
	"FeedbackAnswerUpdateRequest", "FeedbackOrderReturnRequest", "FeedbackOrderReturnResponse", "FeedbackGetRequest",
	"FeedbackGetResponse", "FeedbackArchiveListRequest", "FeedbackArchiveListResponse",
]
