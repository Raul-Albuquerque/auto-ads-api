from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class ReportResponse(BaseModel):
    report_title: str
    generated_at: datetime
    count: Optional[int] = None
    status: Optional[int] = None
    data: Optional[Any] = None
    message: Optional[str] = None
