from wb_api.base.router import Router
from wb_api.generic.functools import cache
from wb_api.const import BaseURL


class FeedbackRouter(Router):
	@cache
	def ping(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/ping"

	@cache
	def new_feedbacks_questions(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/new-feedbacks-questions"

	@cache
	def question_count_unanswered(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/questions/count-unanswered"

	@cache
	def question_count(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/questions/count"

	@cache
	def question_list(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/questions"

	@cache
	def question_mark_as_read(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/questions"

	@cache
	def question_reject(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/questions"

	@cache
	def question_answer_add(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/questions"

	@cache
	def question_answer_update(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/questions"

	@cache
	def question_get(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/question"

	@cache
	def feedback_count_unanswered(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/feedbacks/count-unanswered"

	@cache
	def feedback_count(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/feedbacks/count"

	@cache
	def feedback_list(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/feedbacks"

	@cache
	def feedback_supplier_valuations_get(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/supplier-valuations"

	@cache
	def feedback_text_report(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/feedbacks/actions"

	@cache
	def feedback_product_report(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/feedbacks/actions"

	@cache
	def feedback_answer_add(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/feedbacks/answer"

	@cache
	def feedback_answer_update(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/feedbacks/answer"

	@cache
	def feedback_order_return(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/feedbacks/order/return"

	@cache
	def feedback_get(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/feedback"

	@cache
	def feedback_archived_list(self) -> str:
		return f"{BaseURL.FEEDBACK.value}/api/v1/feedbacks/archive"
