from wb_api.base.async_api_mixin import AsyncAPIMixin
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


class AsyncFeedbackAPI(AsyncAPIMixin, BaseFeedbackAPI):
	async def ping(self) -> PingResponse:
		url = self.router.ping()
		async with self.session.get(url) as response:
			self.validate_response(response)
			return PingResponse.model_validate_json(await response.text())

	async def check_new_feedbacks_questions(self) -> NewFeedbacksQuestionsResponse:
		url = self.router.new_feedbacks_questions()

		async with self.session.get(url) as response:
			self.validate_response(response)
			return NewFeedbacksQuestionsResponse.model_validate_json(await response.text())

	async def get_question_count_unanswered(self) -> QuestionCountUnansweredResponse:
		url = self.router.question_count_unanswered()

		async with self.session.get(url) as response:
			self.validate_response(response)
			return QuestionCountUnansweredResponse.model_validate_json(await response.text())

	async def get_question_count(self, request: Optional[QuestionCountRequest] = None) -> QuestionCountResponse:
		request = request or QuestionCountRequest()
		url = self.router.question_count()

		async with self.session.get(url, params=request.as_request_params()) as response:
			self.validate_response(response)
			return QuestionCountResponse.model_validate_json(await response.text())

	async def get_question_list(self, request: QuestionListRequest) -> QuestionListResponse:
		url = self.router.question_list()

		async with self.session.get(url, params=request.as_request_params()) as response:
			self.validate_response(response)
			return QuestionListResponse.model_validate_json(await response.text())

	async def mark_question_as_read(self, request: QuestionMarkAsReadRequest) -> QuestionMarkAsReadResponse:
		url = self.router.question_mark_as_read()

		async with self.session.patch(url, json=request.as_request_payload()) as response:
			self.validate_response(response)
			return QuestionMarkAsReadResponse.model_validate_json(await response.text())

	async def reject_question(self, request: QuestionRejectRequest) -> QuestionRejectResponse:
		url = self.router.question_reject()

		async with self.session.patch(url, json=request.as_request_payload()) as response:
			self.validate_response(response)
			return QuestionRejectResponse.model_validate_json(await response.text())

	async def add_question_answer(self, request: QuestionAnswerAddRequest) -> QuestionAnswerAddResponse:
		url = self.router.question_answer_add()

		async with self.session.patch(url, json=request.as_request_payload()) as response:
			self.validate_response(response)
			return QuestionAnswerAddResponse.model_validate_json(await response.text())

	async def update_question_answer(self, request: QuestionAnswerUpdateRequest) -> QuestionAnswerUpdateResponse:
		url = self.router.question_answer_update()

		async with self.session.patch(url, json=request.as_request_payload()) as response:
			self.validate_response(response)
			return QuestionAnswerUpdateResponse.model_validate_json(await response.text())

	async def get_question(self, request: QuestionGetRequest) -> QuestionGetResponse:
		url = self.router.question_get()

		async with self.session.get(url, params=request.as_request_params()) as response:
			self.validate_response(response)
			return QuestionGetResponse.model_validate_json(await response.text())

	async def get_feedback_count_unanswered(self) -> FeedbackCountUnansweredResponse:
		url = self.router.feedback_count_unanswered()

		async with self.session.get(url) as response:
			self.validate_response(response)
			return FeedbackCountUnansweredResponse.model_validate_json(await response.text())

	async def get_feedback_count(self, request: Optional[FeedbackCountRequest] = None) -> FeedbackCountResponse:
		request = request or FeedbackCountRequest()
		url = self.router.feedback_count()

		async with self.session.get(url, params=request.as_request_params()) as response:
			self.validate_response(response)
			return FeedbackCountResponse.model_validate_json(await response.text())

	async def get_feedback_list(self, request: FeedbackListRequest) -> FeedbackListResponse:
		url = self.router.feedback_list()

		async with self.session.get(url, params=request.as_request_params()) as response:
			self.validate_response(response)
			return FeedbackListResponse.model_validate_json(await response.text())

	async def get_feedback_supplier_valuations(
		self,
		request: Optional[FeedbackSupplierValuationsRequest] = None,
	) -> FeedbackSupplierValuationsResponse:
		request = request or FeedbackSupplierValuationsRequest()
		url = self.router.feedback_supplier_valuations_get()

		async with self.session.get(url, headers=request.as_request_headers()) as response:
			self.validate_response(response)
			return FeedbackSupplierValuationsResponse.model_validate_json(await response.text())

	async def report_feedback_text(self, request: FeedbackTextReportRequest) -> None:
		url = self.router.feedback_text_report()

		async with self.session.post(url, json=request.as_request_payload()) as response:
			self.validate_response(response, HTTPStatus.NO_CONTENT)
			return None

	async def report_feedback_product(self, request: FeedbackProductReportRequest) -> None:
		url = self.router.feedback_product_report()

		async with self.session.post(url, json=request.as_request_payload()) as response:
			self.validate_response(response, HTTPStatus.NO_CONTENT)
			return None

	async def add_feedback_answer(self, request: FeedbackAnswerAddRequest) -> None:
		url = self.router.feedback_answer_add()

		async with self.session.post(url, json=request.as_request_payload()) as response:
			self.validate_response(response, HTTPStatus.NO_CONTENT)
			return None

	async def update_feedback_answer(self, request: FeedbackAnswerUpdateRequest) -> None:
		url = self.router.feedback_answer_update()

		async with self.session.patch(url, json=request.as_request_payload()) as response:
			self.validate_response(response, HTTPStatus.NO_CONTENT)
			return None

	async def return_feedback_order(self, request: FeedbackOrderReturnRequest) -> FeedbackOrderReturnResponse:
		url = self.router.feedback_order_return()

		async with self.session.post(url, json=request.as_request_payload()) as response:
			self.validate_response(response)
			return FeedbackOrderReturnResponse.model_validate_json(await response.text())

	async def get_feedback(self, request: FeedbackGetRequest) -> FeedbackGetResponse:
		url = self.router.feedback_get()

		async with self.session.get(url, params=request.as_request_params()) as response:
			self.validate_response(response)
			return FeedbackGetResponse.model_validate_json(await response.text())

	async def get_feedback_archive_list(self, request: FeedbackArchiveListRequest) -> FeedbackArchiveListResponse:
		url = self.router.feedback_archived_list()

		async with self.session.get(url, params=request.as_request_params()) as response:
			self.validate_response(response)
			return FeedbackArchiveListResponse.model_validate_json(await response.text())
