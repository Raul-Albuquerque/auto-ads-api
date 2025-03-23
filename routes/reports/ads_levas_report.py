from datetime import datetime
from fastapi import APIRouter

from models.report_models import ReportResponse
from services.utmify import get_campaigns

router = APIRouter()

@router.get("/ads/report/levas/{day}")
def get_all_ads(day:str):
  name_contains = None

  try:
    response = get_campaigns(day=day, name_contains=name_contains)
    ads = response.get("results")
    return ads

  except Exception as e:
    return ReportResponse(report_title="Get All Purchases", generated_at=datetime.now(), data={"Error": str(e)})