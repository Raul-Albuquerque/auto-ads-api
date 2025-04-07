import pytz
from datetime import datetime
from fastapi import APIRouter

from models.report_models import ReportResponse
from models.header_campaigns_list import header_campaigns
from services.utmify import get_campaigns
from services.google_sheets import open_spreadsheet, search_worksheet_index

router = APIRouter()
timezone = pytz.timezone("America/Sao_Paulo")
local_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

@router.get("/utmify/campaigns/{day}")
def get_all_ads(day:str):
  name_contains = None

  try:
    response = get_campaigns(day=day, name_contains=name_contains, products=None, level="campaign")

    if response.status == 400:
      print(response.message)
      return ReportResponse(report_title="Write Utmify Campaigns - Error", generated_at=datetime.now(), message=response.message, status=response.status)

    ads = response.data
    if len(ads) < 1:
      print(response.message)
      return ReportResponse(report_title="Write Utmify Campaigns - Error", generated_at=datetime.now(), message=response.message, status=response.status)
  
    def convert_to_list_of_lists(data):
      return [list(item.values()) for item in data]

    header = header_campaigns
    values_to_write = convert_to_list_of_lists(ads)
    values_to_write.insert(0, header)
    spreadsheet = open_spreadsheet("DB_3.0", "1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz")
    worksheet_index = search_worksheet_index("DB_3.0", "1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz", "RAW-CAMPAIGNS")
    worksheet = spreadsheet.get_worksheet(worksheet_index)
    worksheet.clear()
    next_row = 1
    worksheet.update(f"A{next_row}:ZZ{next_row + len(values_to_write) - 1}", values_to_write)
    return ReportResponse(report_title="Write Utmify Campaigns - Success", generated_at=datetime.now(), message="Os dados dos anúncios foram escritos com sucesso!", status=200)

  except Exception as e:
    return ReportResponse(report_title="Write Utmify Campaigns - Error", generated_at=datetime.now(), message=f"Error: {str(e)}", status=400)