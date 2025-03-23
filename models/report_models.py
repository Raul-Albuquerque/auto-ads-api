from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

class ReportResponse(BaseModel):
  report_title: str
  generated_at: datetime
  count: Optional[int] = None
  data: Any