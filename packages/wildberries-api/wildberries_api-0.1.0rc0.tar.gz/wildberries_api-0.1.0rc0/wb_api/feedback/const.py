from enum import Enum


class QuestionState(Enum):
	REJECTED = "none"
	ACCEPTED = "wbRu"
	NEW = "suppliersPortalSynch"


class FeedbackState(Enum):
	NEW = "none"
	PROCESSED = "wbRu"


class FeedbackAnswerState(Enum):
	NEW = "none"
	ACCEPTED = "wbRu"
	ON_REVIEW = "reviewRequired"
	REJECTED = "rejected"


class MatchingSize(Enum):
	DIMENSIONLESS = ""
	MATCH = "ok"
	UNDERSIZED = "smaller"
	OVERSIZED = "bigger"
