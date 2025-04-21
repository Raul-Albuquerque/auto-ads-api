from datetime import datetime
from fastapi import APIRouter, Depends

from auth import get_api_key
from app.models.report_model import ReportResponse
from app.models.payload_models import AdsControlReport
from app.domain.reports.ads_d2d_report import ads_d2d_report, all_ads_d2d_report
from app.external_services.gmail import send_email
from app.core.helpers import delete_reports_folder

router = APIRouter()


@router.post("/d2d")
async def write_ads_d2d(filters: AdsControlReport, api_key: str = Depends(get_api_key)):
    try:
        if filters.active_offer != "all":
            try:
                ads_d2d_report(
                    report_type=filters.report_type, active_offer=filters.active_offer
                )
            except Exception as e:
                print(e)
        else:
            try:
                all_ads_d2d_report(report_type=filters.report_type)
            except Exception as e:
                print(e)
        send_email("Ads Escalados (d2d)")
        delete_reports_folder()
        return ReportResponse(
            report_title="Write Ads Escalados (d2d) - Success",
            generated_at=datetime.now(),
            message=f"Ads Escalados (d2d) escrito com sucesso!",
            status=200,
        )
    except Exception as e:
        return ReportResponse(
            report_title="Write Ads Escalados (d2d) - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )
