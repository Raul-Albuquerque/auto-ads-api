import pytz
from datetime import datetime
from fastapi import APIRouter

from models.report_models import ReportResponse
from services.vturb import call_vturb_stats

router = APIRouter()
timezone = pytz.timezone("America/Sao_Paulo")
local_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

@router.get("/vturb/all")
def get_all_ads():

  try:
    response = call_vturb_stats()
    return response
    

    # header = header_ads
    # values_to_write = convert_to_list_of_lists(ads)
    # values_to_write.insert(0, header)
    # spreadsheet = open_spreadsheet("DB_3.0", "1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz")
    # worksheet_index = search_worksheet_index("DB_3.0", "1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz", "RAW")
    # worksheet = spreadsheet.get_worksheet(worksheet_index)
    # worksheet.clear()
    # next_row = 1
    # worksheet.update(f"A{next_row}:ZZ{next_row + len(values_to_write) - 1}", values_to_write)
    # return ReportResponse(report_title="Write Utmify Ads - Success", generated_at=datetime.now(), message="Os dados dos anúncios foram escritos com sucesso!", status=200)

  except Exception as e:
    return ReportResponse(report_title="Write Utmify Ads - Error", generated_at=datetime.now(), message=f"Error: {str(e)}", status=400)