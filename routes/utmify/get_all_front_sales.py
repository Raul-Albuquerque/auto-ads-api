import pytz
from datetime import datetime
from fastapi import APIRouter

from models.report_models import ReportResponse
from models.header_ads_list import header_ads
from models.front_products_list import front_products_list
from services.utmify import get_campaigns
from services.google_sheets import open_spreadsheet, search_worksheet_index

router = APIRouter()
timezone = pytz.timezone("America/Sao_Paulo")
local_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

@router.get("/utmify/sales/{day}")
def get_all_ads(day:str):
  name_contains = None

  try:
    ads = get_campaigns(day=day, name_contains=name_contains, products=front_products_list)
    def convert_to_list_of_lists(data):
      return [list(item.values()) for item in data]

    ads_list = convert_to_list_of_lists(ads)
    values_to_write = [lista[9] for lista in ads_list]
    spreadsheet = open_spreadsheet("DB_3.0", "1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz")
    worksheet_index = search_worksheet_index("DB_3.0", "1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz", "RAW")
    worksheet = spreadsheet.get_worksheet(worksheet_index)
    next_row = 2
    worksheet.update(f"J{next_row}:J{next_row + len(values_to_write) - 1}", [[value] for value in values_to_write])
    return ReportResponse(report_title="Get All Purchases - write purchases", generated_at=local_time, count=len(values_to_write), data={"Status": "Os dados foram escritos com sucesso!"})

  except Exception as e:
    return ReportResponse(report_title="Get All Purchases", generated_at=datetime.now(), data={"Error": str(e)})