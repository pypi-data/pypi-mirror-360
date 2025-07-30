from wb_api.base.api import API
from wb_api.feedback.router import FeedbackRouter


class BaseFeedbackAPI(API[FeedbackRouter]):
	@staticmethod
	def make_router():
		return FeedbackRouter()
