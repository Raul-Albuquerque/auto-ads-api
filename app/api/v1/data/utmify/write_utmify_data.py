from datetime import datetime
from fastapi import APIRouter, Depends

from auth import get_api_key
from app.models.report_model import ReportResponse
from app.models.payload_models import UtmifyFilters
from app.external_services.utmify import get_data
from app.static_data.spreadsheet_header import spreadsheet_header
from app.external_services.google_sheets import open_spreadsheet, search_worksheet_index
from config import (
    TIMEZONE,
    DB_SPREADSHEET,
    DB_SPREADSHEET_FOLDER_ID,
    REPORT_TYPE_DATA_WORKSHEETS,
)

router = APIRouter()


@router.post("/utmify")
async def write_utmify_data(
    filters: UtmifyFilters, api_key: str = Depends(get_api_key)
):
    level = filters.level
    report_type = filters.report_type
    period = filters.period
    worksheet_name = REPORT_TYPE_DATA_WORKSHEETS[report_type]

    try:
        response = get_data(day=period, products=None, level=level, name_contains=None)
        print(response.status)

        if response.status == 400:
            print(response.message)
            return ReportResponse(
                report_title="Write Utmify Ads - Error",
                generated_at=datetime.now(),
                message=response.message,
                status=response.status,
            )

        ads = response.data
        if len(ads) < 1:
            print(response.message)
            return ReportResponse(
                report_title="Write Utmify Ads - Error",
                generated_at=datetime.now(TIMEZONE),
                message=response.message,
                status=response.status,
            )

        def convert_to_list_of_lists(data):
            return [list(item.values()) for item in data]

        values_to_write = convert_to_list_of_lists(ads)
        values_to_write.insert(0, spreadsheet_header)
        spreadsheet = open_spreadsheet(DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID)
        worksheet_index = search_worksheet_index(
            DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID, worksheet_name
        )
        worksheet = spreadsheet.get_worksheet(worksheet_index)
        worksheet.clear()
        next_row = 1
        worksheet.update(
            f"A{next_row}:ZZ{next_row + len(values_to_write) - 1}", values_to_write
        )
        return ReportResponse(
            report_title="Write Utmify Data - Success",
            generated_at=datetime.now(TIMEZONE),
            message="Os dados foram escritos com sucesso!",
            status=200,
        )

    except Exception as e:
        return ReportResponse(
            report_title="Write Utmify data - Error",
            generated_at=datetime.now(TIMEZONE),
            message=f"Error: {str(e)}",
            status=400,
        )
