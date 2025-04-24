from datetime import datetime
from fastapi import APIRouter, Depends

from auth import get_api_key
from app.models.report_model import ReportResponse
from app.models.payload_models import TrafficControlReport
from app.domain.reports.traffic_control import all_traffic_report

router = APIRouter()


@router.post("/trafego")
async def write_traffic_control(
    filters: TrafficControlReport, api_key: str = Depends(get_api_key)
):
    try:
        data = await all_traffic_report(ad_plataform=filters.plataform)
        return data
    except Exception as e:
        print(e)
