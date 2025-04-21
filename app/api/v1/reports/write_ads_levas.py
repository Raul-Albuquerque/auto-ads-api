from datetime import datetime
from fastapi import APIRouter, Depends

from auth import get_api_key
from app.models.report_model import ReportResponse
from app.models.payload_models import AdsControlReport
from app.domain.reports.ads_levas_report import ads_levas_report, all_ads_levas_report
from app.external_services.gmail import send_email
from app.core.helpers import delete_reports_folder

router = APIRouter()


@router.post("/levas")
async def write_ads_levas(
    filters: AdsControlReport, api_key: str = Depends(get_api_key)
):
    try:
        if filters.active_offer != "all":
            try:
                ads_levas_report(
                    active_offer=filters.active_offer, report_type=filters.report_type
                )
            except Exception as e:
                print(e)
        else:
            try:
                all_ads_levas_report(report_type=filters.report_type)
            except Exception as e:
                print(e)
        send_email("Relatórios de Ads Levas")
        delete_reports_folder()
        return ReportResponse(
            report_title="Write Ads (levas) - Success",
            generated_at=datetime.now(),
            message=f"Relatórios de Ads (levas) escrito com sucesso!",
            status=200,
        )
    except Exception as e:
        return ReportResponse(
            report_title="Write Ads Levas of all offers - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )
