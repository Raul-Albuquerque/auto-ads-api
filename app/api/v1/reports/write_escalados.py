from datetime import datetime
from fastapi import APIRouter, Depends

from auth import get_api_key
from app.models.report_model import ReportResponse
from app.models.payload_models import EscaladosReport
from app.domain.reports.escalados_report import (
    all_ads_escalados_report,
    ads_escalados_report,
)
from app.external_services.gmail import send_email
from app.core.helpers import delete_reports_folder

router = APIRouter()


@router.post("/escalados")
async def write_ads_escalados(
    filters: EscaladosReport, api_key: str = Depends(get_api_key)
):
    try:
        if filters.active_offer != "all":
            try:
                ads_escalados_report(
                    active_offer=filters.active_offer,
                    report_type=filters.report_type,
                    period=filters.period,
                )
            except Exception as e:
                print(e)
        else:
            try:
                all_ads_escalados_report(
                    report_type=filters.report_type, period=filters.period
                )
            except Exception as e:
                print(e)
        send_email("Relatórios de Ads Escalados")
        delete_reports_folder()
        return ReportResponse(
            report_title="Write Ads Escalados - Success",
            generated_at=datetime.now(),
            message=f"Relatórios de Ads Escalados escrito com sucesso!",
            status=200,
        )
    except Exception as e:
        return ReportResponse(
            report_title="Write Ads Escalados of all offers - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )
