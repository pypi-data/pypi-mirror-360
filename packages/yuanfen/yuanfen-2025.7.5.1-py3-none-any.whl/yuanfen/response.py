from pydantic import BaseModel
from typing import Optional, Any


class BaseResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class SuccessResponse(BaseResponse):
    code: int = 0
    message: str = "SUCCESS"


class ErrorResponse(BaseResponse):
    code: int = 1000
    message: str = "ERROR"
