import requests
from datetime import datetime
from fastapi import APIRouter, Depends

from auth import get_api_key
from app.models.payload_models import VturbFilters
from app.models.report_model import ReportResponse
from app.external_services.vturb import get_all_player_data
from app.core.helpers import get_date_range, convert_stats_to_list, get_all_players_id
from app.external_services.google_sheets import open_spreadsheet, search_worksheet_index
from config import (
    TIMEZONE,
    DB_SPREADSHEET,
    DB_SPREADSHEET_FOLDER_ID,
    REPORT_TYPE_DATA_WORKSHEETS,
)

router = APIRouter()


@router.post("/vturb")
def write_player_stats(filters: VturbFilters, api_key: str = Depends(get_api_key)):
    url = f"https://pureessentialsshops.com/report/{filters.period}"
    try:
        response = requests.get(url)
        data = response.json().get("data")
        worksheet_name = REPORT_TYPE_DATA_WORKSHEETS[filters.report_type]
        values_to_write = convert_stats_to_list(data)
        values_to_write.insert(
            0,
            [
                "Player_id",
                "Name",
                "TotalUniqDeviceEvents",
                "Total_over_pitch",
                "Total_under_pitch",
                "Error",
            ],
        )

        spreadsheet = open_spreadsheet(DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID)
        worksheet_index = search_worksheet_index(
            DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID, worksheet_name
        )
        worksheet = spreadsheet.get_worksheet(worksheet_index)
        worksheet.clear()
        next_row = 1
        worksheet.update(
            f"A{next_row}:F{next_row + len(values_to_write) - 1}", values_to_write
        )
        return ReportResponse(
            report_title="Write Players Stats - Success",
            generated_at=datetime.now(TIMEZONE),
            message="Os dados foram escritos com sucesso!",
            status=200,
        )

    except Exception as e:
        return ReportResponse(
            report_title="Write Players Stats - Error",
            generated_at=datetime.now(TIMEZONE),
            message=f"Error: {str(e)}",
            status=400,
        )
