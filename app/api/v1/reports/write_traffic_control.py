from datetime import datetime
from fastapi import APIRouter, Depends

from auth import get_api_key
from app.models.report_model import ReportResponse
from app.models.payload_models import TrafficControlReport
from app.domain.reports.traffic_control import traffic_report, all_traffic_report

router = APIRouter()


@router.post("/trafego")
async def write_traffic_control(
    filters: TrafficControlReport, api_key: str = Depends(get_api_key)
):
    try:
        if filters.active_offer != "all":
            await traffic_report(
                active_offer=filters.active_offer,
                report_type=filters.report_type,
                day=filters.period,
            )

        else:
            await all_traffic_report(
                report_type=filters.report_type,
                day=filters.period,
            )

        return ReportResponse(
            report_title="Write Leads - Success",
            generated_at=datetime.now(),
            message=f"Controle de Tráfego escrito com sucesso!",
            status=200,
        )
    except Exception as e:
        return ReportResponse(
            report_title="Controle de Tráfego escrito com sucesso!",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )
