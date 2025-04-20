from datetime import datetime
from fastapi import APIRouter, Depends

from auth import get_api_key
from app.models.report_model import ReportResponse
from app.models.payload_models import AdsControlReport
from app.domain.reports.ads_agregado_report import (
    ads_agregado_report,
    all_ads_agregado_report,
)

router = APIRouter()


@router.post("/agregado")
async def write_ads_agregado(
    filters: AdsControlReport, api_key: str = Depends(get_api_key)
):
    try:
        if filters.active_offer != "all":
            try:
                ads_agregado_report(
                    active_offer=filters.active_offer, report_type=filters.report_type
                )
            except Exception as e:
                print(e)
        else:
            try:
                all_ads_agregado_report(report_type=filters.report_type)
            except Exception as e:
                print(e)
        return ReportResponse(
            report_title="Write Ads Escalados (Agreg.) - Success",
            generated_at=datetime.now(),
            message=f"Relatórios de Ads Escalados (Agreg.) escrito com sucesso!",
            status=200,
        )

    except Exception as e:
        return ReportResponse(
            report_title="Write Ads Levas of all offers - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )
