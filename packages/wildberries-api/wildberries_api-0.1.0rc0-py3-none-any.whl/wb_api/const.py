from enum import Enum


class BaseURL(Enum):
	COMMON = "https://common-api.wildberries.ru"
	FEEDBACK = "https://feedbacks-api.wildberries.ru"


class Header(Enum):
	AUTHORIZATION = "Authorization"
	LOCALE = "X-Locale"
