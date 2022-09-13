from pydantic import BaseModel


class ErrorModel(BaseModel):
    status_code: int
    error_code: int
    error_msg: str
