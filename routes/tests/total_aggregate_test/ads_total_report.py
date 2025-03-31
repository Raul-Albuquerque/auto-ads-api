import pytz, os,csv
from datetime import datetime
from fastapi import APIRouter
import pandas as pd
import numpy as np

from models.report_models import ReportResponse
from models.active_offers_info import active_offers_info
from core.helpers import delete_reports_folder
from services.gmail import send_email
from core.cleaners import extract_ad_name, extract_offer_name
from core.numbers_cleaners import currency_to_int, str_to_int, int_to_currency
from services.google_sheets import open_spreadsheet, search_worksheet_index

router = APIRouter()

timezone = pytz.timezone("America/Sao_Paulo")
spreadsheet_db_id="1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz"
spreadsheet_active_offers_id="1z3YUtEjHVH5t5tppLyzSnw972WRbbDcG"

@router.get("/ads/report/total")
def write_ads_total_report():
  raw_local_time = datetime.now(timezone)
  local_time = raw_local_time.strftime("%d/%m/%Y às %Hh%Mmin%Ss")

  try:
    ads_spreadsheet = open_spreadsheet("DB_3.0", spreadsheet_db_id)
    ads_worksheet_index = search_worksheet_index("DB_3.0", spreadsheet_db_id, "RAW")
    ads_worksheet = ads_spreadsheet.get_worksheet(ads_worksheet_index)
    ads = ads_worksheet.get_all_values()
    ads_df = pd.DataFrame(ads)
    ads_df = ads_df.drop(ads_df.columns[[0,1,2,3,4,5,6,7,8,10,11,12,14,15,16,17,19,20,21,22,23,25,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61]], axis=1)
    ads_df[9] = ads_df[9].replace('', '0').astype(str).apply(str_to_int) # SALES
    ads_df[18] = ads_df[18].replace('', '0').astype(str).apply(str_to_int) # REVENUE
    ads_df[27] = ads_df[27].replace('', '0').astype(str).apply(str_to_int) # SPEND
    ads_df[24] = ads_df[24].replace('', '0').astype(str).apply(str_to_int) # IMPRESSIONS
    ads_df[26] = ads_df[26].replace('', '0').astype(str).apply(str_to_int) # INLINELINKCLICKS
    ads_df[45] = ads_df[45].replace('', '0').astype(str).apply(str_to_int) # VIDEOVIEWS3S
    ads_df[62] = ads_df[13].replace('', '0').astype(str).apply(extract_ad_name) # AD NAME
    ads_df[63] = ads_df[13].replace('', '0').astype(str).apply(extract_offer_name) # OFFER
    ads_group = ads_df.groupby(62).apply(lambda x: x.values.tolist())
    offer_group = ads_df.groupby(63).apply(lambda x: x.values.tolist())

    sales_spreadsheet = open_spreadsheet("DB_3.0", spreadsheet_db_id)
    sales_worksheet_index = search_worksheet_index("DB_3.0", spreadsheet_db_id, "RAW-SALES")
    sales_worksheet = sales_spreadsheet.get_worksheet(sales_worksheet_index)
    all_sales = sales_worksheet.get_all_values()
    all_sales_df = pd.DataFrame(all_sales)
    all_sales_df[9] = all_sales_df[9].replace('', '0').astype(str).apply(str_to_int) # SALES
    all_sales_df[62] = all_sales_df[13].replace('', '0').astype(str).apply(extract_ad_name) # AD NAME
    all_sales_df[63] = all_sales_df[13].replace('', '0').astype(str).apply(extract_offer_name) # OFFER
    all_sales_df = all_sales_df.drop(all_sales_df.columns[[0,1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61]], axis=1)
    sales_ads_group = all_sales_df.groupby(62).apply(lambda x: x.values.tolist())

    trafic_spreadsheet = open_spreadsheet("LVH_ESP", spreadsheet_active_offers_id)
    ads_total_worksheet_index = search_worksheet_index("LVH_ESP", spreadsheet_active_offers_id, "Ads Escalados (Agreg.)")
    ads_total_worksheet = trafic_spreadsheet.get_worksheet(ads_total_worksheet_index)
    ads_total_worksheet_data = ads_total_worksheet.get_all_values()
    ads_total_df = pd.DataFrame(ads_total_worksheet_data)
    ads_total_df[2] = ads_total_df[2].astype(str).apply(currency_to_int) # INVESTIDO
    ads_total_df[3] = ads_total_df[3].astype(str).apply(currency_to_int) # FATURAMENTO
    ads_total_df[6] = ads_total_df[6].astype(str).apply(str_to_int) # vendas
    ads_total_list = ads_total_df.values.tolist()
    return {"ads": ads_total_list}

    for item in active_offers_info:
      print("new")

  except Exception as e:
    return ReportResponse(report_title="Write Ads Levas of all offers - Error", generated_at=datetime.now(), message=f"Error: {str(e)}", status=400)