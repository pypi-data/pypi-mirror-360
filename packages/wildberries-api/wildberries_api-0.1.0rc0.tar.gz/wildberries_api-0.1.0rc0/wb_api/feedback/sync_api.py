from wb_api.base.sync_api_mixin import SyncAPIMixin
from wb_api.feedback.base_api import BaseFeedbackAPI
from wb_api.base.dataclass import PingResponse
from wb_api.feedback.dataclass import (
	NewFeedbacksQuestionsResponse, QuestionCountUnansweredResponse, QuestionCountRequest, QuestionCountResponse,
	QuestionListRequest, QuestionListResponse, QuestionMarkAsReadRequest, QuestionMarkAsReadResponse,
	QuestionRejectRequest, QuestionRejectResponse, QuestionAnswerAddRequest, QuestionAnswerAddResponse,
	QuestionAnswerUpdateRequest, QuestionAnswerUpdateResponse, QuestionGetRequest, QuestionGetResponse,
	FeedbackCountUnansweredResponse, FeedbackCountRequest, FeedbackCountResponse, FeedbackListRequest,
	FeedbackListResponse, FeedbackSupplierValuationsRequest, FeedbackSupplierValuationsResponse,
	FeedbackTextReportRequest, FeedbackProductReportRequest, FeedbackAnswerAddRequest, FeedbackAnswerUpdateRequest,
	FeedbackOrderReturnRequest, FeedbackOrderReturnResponse, FeedbackGetRequest, FeedbackGetResponse,
	FeedbackArchiveListRequest, FeedbackArchiveListResponse,
)

from typing import Optional
from http import HTTPStatus


class SyncFeedbackAPI(SyncAPIMixin, BaseFeedbackAPI):
	def ping(self) -> PingResponse:
		url = self.router.ping()
		response = self.session.get(url)
		self.validate_response(response)
		return PingResponse.model_validate_json(response.text)

	def check_new_feedbacks_questions(self) -> NewFeedbacksQuestionsResponse:
		url = self.router.new_feedbacks_questions()
		response = self.session.get(url)
		self.validate_response(response)
		return NewFeedbacksQuestionsResponse.model_validate_json(response.text)

	def get_question_count_unanswered(self) -> QuestionCountUnansweredResponse:
		url = self.router.question_count_unanswered()
		response = self.session.get(url)
		self.validate_response(response)
		return QuestionCountUnansweredResponse.model_validate_json(response.text)

	def get_question_count(self, request: Optional[QuestionCountRequest] = None) -> QuestionCountResponse:
		request = request or QuestionCountRequest()
		url = self.router.question_count()
		response = self.session.get(url, params=request.as_request_params())
		self.validate_response(response)
		return QuestionCountResponse.model_validate_json(response.text)

	def get_question_list(self, request: QuestionListRequest) -> QuestionListResponse:
		url = self.router.question_list()
		response = self.session.get(url, params=request.as_request_params())
		self.validate_response(response)
		return QuestionListResponse.model_validate_json(response.text)

	def mark_question_as_read(self, request: QuestionMarkAsReadRequest) -> QuestionMarkAsReadResponse:
		url = self.router.question_mark_as_read()
		response = self.session.patch(url, json=request.as_request_payload())
		self.validate_response(response)
		return QuestionMarkAsReadResponse.model_validate_json(response.text)

	def reject_question(self, request: QuestionRejectRequest) -> QuestionRejectResponse:
		url = self.router.question_reject()
		response = self.session.patch(url, json=request.as_request_payload())
		self.validate_response(response)
		return QuestionRejectResponse.model_validate_json(response.text)

	def add_question_answer(self, request: QuestionAnswerAddRequest) -> QuestionAnswerAddResponse:
		url = self.router.question_answer_add()
		response = self.session.patch(url, json=request.as_request_payload())
		self.validate_response(response)
		return QuestionAnswerAddResponse.model_validate_json(response.text)

	def update_question_answer(self, request: QuestionAnswerUpdateRequest) -> QuestionAnswerUpdateResponse:
		url = self.router.question_answer_update()
		response = self.session.patch(url, json=request.as_request_payload())
		self.validate_response(response)
		return QuestionAnswerUpdateResponse.model_validate_json(response.text)

	def get_question(self, request: QuestionGetRequest) -> QuestionGetResponse:
		url = self.router.question_get()
		response = self.session.get(url, params=request.as_request_params())
		self.validate_response(response)
		return QuestionGetResponse.model_validate_json(response.text)

	def get_feedback_count_unanswered(self) -> FeedbackCountUnansweredResponse:
		url = self.router.feedback_count_unanswered()
		response = self.session.get(url)
		self.validate_response(response)
		return FeedbackCountUnansweredResponse.model_validate_json(response.text)

	def get_feedback_count(self, request: Optional[FeedbackCountRequest] = None) -> FeedbackCountResponse:
		request = request or FeedbackCountRequest()
		url = self.router.feedback_count()
		response = self.session.get(url, params=request.as_request_params())
		self.validate_response(response)
		return FeedbackCountResponse.model_validate_json(response.text)

	def get_feedback_list(self, request: FeedbackListRequest) -> FeedbackListResponse:
		url = self.router.feedback_list()
		response = self.session.get(url, params=request.as_request_params())
		self.validate_response(response)
		return FeedbackListResponse.model_validate_json(response.text)

	def get_feedback_supplier_valuations(
		self,
		request: Optional[FeedbackSupplierValuationsRequest] = None,
	) -> FeedbackSupplierValuationsResponse:
		request = request or FeedbackSupplierValuationsRequest()
		url = self.router.feedback_supplier_valuations_get()
		response = self.session.get(url, headers=request.as_request_headers())
		self.validate_response(response)
		return FeedbackSupplierValuationsResponse.model_validate_json(response.text)

	def report_feedback_text(self, request: FeedbackTextReportRequest) -> None:
		url = self.router.feedback_text_report()
		response = self.session.post(url, json=request.as_request_payload())
		self.validate_response(response, HTTPStatus.NO_CONTENT)
		return None

	def report_feedback_product(self, request: FeedbackProductReportRequest) -> None:
		url = self.router.feedback_product_report()
		response = self.session.post(url, json=request.as_request_payload())
		self.validate_response(response, HTTPStatus.NO_CONTENT)
		return None

	def add_feedback_answer(self, request: FeedbackAnswerAddRequest) -> None:
		url = self.router.feedback_answer_add()
		response = self.session.post(url, json=request.as_request_payload())
		self.validate_response(response, HTTPStatus.NO_CONTENT)
		return None

	def update_feedback_answer(self, request: FeedbackAnswerUpdateRequest) -> None:
		url = self.router.feedback_answer_update()
		response = self.session.patch(url, json=request.as_request_payload())
		self.validate_response(response, HTTPStatus.NO_CONTENT)
		return None

	def return_feedback_order(self, request: FeedbackOrderReturnRequest) -> FeedbackOrderReturnResponse:
		url = self.router.feedback_order_return()
		response = self.session.post(url, json=request.as_request_payload())
		self.validate_response(response)
		return FeedbackOrderReturnResponse.model_validate_json(response.text)

	def get_feedback(self, request: FeedbackGetRequest) -> FeedbackGetResponse:
		url = self.router.feedback_get()
		response = self.session.get(url, params=request.as_request_params())
		self.validate_response(response)
		return FeedbackGetResponse.model_validate_json(response.text)

	def get_feedback_archive_list(self, request: FeedbackArchiveListRequest) -> FeedbackArchiveListResponse:
		url = self.router.feedback_archived_list()
		response = self.session.get(url, params=request.as_request_params())
		self.validate_response(response)
		return FeedbackArchiveListResponse.model_validate_json(response.text)
