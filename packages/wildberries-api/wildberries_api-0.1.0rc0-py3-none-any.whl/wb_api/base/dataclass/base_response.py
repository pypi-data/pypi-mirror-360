from typing import Any, Optional, List

from pydantic.main import BaseModel
from pydantic.fields import Field


class BaseResponse(BaseModel):
	data: Any
	error: bool
	error_text: str = Field(validation_alias="errorText")
	additional_errors: Optional[List[str]] = Field(validation_alias="additionalErrors")
