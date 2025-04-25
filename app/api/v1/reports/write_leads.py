from datetime import datetime
from fastapi import APIRouter, Depends

from auth import get_api_key
from app.models.payload_models import LeadsReport
from app.models.report_model import ReportResponse
from app.domain.reports.leads_report import all_leads_report, leads_report
from app.external_services.gmail import send_email
from app.core.helpers import delete_reports_folder

router = APIRouter()


@router.post("/leads")
async def write_leads(filters: LeadsReport, api_key: str = Depends(get_api_key)):
    try:
        if filters.active_offer != "all":
            try:
                leads_report(
                    report_type=filters.report_type,
                    period=filters.period,
                    active_offer=filters.active_offer,
                )
            except Exception as e:
                print(e)
        else:
            try:
                all_leads_report(report_type=filters.report_type, period=filters.period)
            except Exception as e:
                print(e)

        send_email("Relatórios de Leads")
        delete_reports_folder()
        return ReportResponse(
            report_title="Write Leads - Success",
            generated_at=datetime.now(),
            message=f"Relatórios de Leads escrito com sucesso!",
            status=200,
        )
    except Exception as e:
        return ReportResponse(
            report_title="Write Ads Levas of all offers - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )
