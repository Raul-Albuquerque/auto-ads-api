import pytz
from datetime import datetime, timedelta
from fastapi import APIRouter
import pandas as pd

from models.report_models import ReportResponse
from core.helpers import deduplicate_leads_group, delete_reports_folder
from core.reports_functions import generate_daily_report, generate_consolidated_report
from services.gmail import send_email
from core.cleaners import extract_lead_info, extract_ad_block, extract_lead_block, extract_ad_lead
from core.numbers_cleaners import str_to_int
from services.google_sheets import open_spreadsheet, search_worksheet_index

router = APIRouter()

timezone = pytz.timezone("America/Sao_Paulo")
spreadsheet_db_id="1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz"
spreadsheet_leads_folder_id="1ctHfPVHVF13Mg_PknwZo1NwSHYzxUoe6"

@router.get("/test/ads/leads")
def write_ads_lead_report():
  raw_local_time = datetime.now(timezone) - timedelta(days=1)
  local_date = raw_local_time.strftime("%d/%m/%Y")

  try:
    sales_spreadsheet = open_spreadsheet("DB_3.0", spreadsheet_db_id)
    sales_worksheet_index = search_worksheet_index("DB_3.0", spreadsheet_db_id, "RAW-CAMPAIGNS-SALES")
    sales_worksheet = sales_spreadsheet.get_worksheet(sales_worksheet_index)
    all_sales = sales_worksheet.get_all_values()
    all_sales_df = pd.DataFrame(all_sales)
    all_sales_df[9] = all_sales_df[9].replace('', '0').astype(str).apply(str_to_int) # SALES
    all_sales_df = all_sales_df.drop(all_sales_df.columns[[0,1,2,4,5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61]], axis=1)
    sales_ads_list = all_sales_df.groupby(3).apply(lambda x: x.values.tolist())

    campaigns_spreadsheet = open_spreadsheet("DB_3.0", spreadsheet_db_id)
    campaigns_worksheet_index = search_worksheet_index("DB_3.0", spreadsheet_db_id, "RAW-CAMPAIGNS")
    campaigns_worksheet = campaigns_spreadsheet.get_worksheet(campaigns_worksheet_index)
    campaigns = campaigns_worksheet.get_all_values()
    for campaign in campaigns[1:]:
      campaign_id = campaign[3]
      campaign[9] = sales_ads_list[campaign_id][0][1]
    ads_df = pd.DataFrame(campaigns)
    ads_df = ads_df.drop(ads_df.columns[[0,1,2,4,5,6,7,8,10,11,12,14,15,16,17,19,20,21,22,23,24,25,26,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61]], axis=1)
    ads_df[18] = ads_df[18].replace('', '0').astype(str).apply(str_to_int) # REVENUE
    ads_df[27] = ads_df[27].replace('', '0').astype(str).apply(str_to_int) # SPEND
    ads_df[62] = ads_df[13].replace("", "0").astype(str).apply(extract_lead_info) # FULL LEAD NAME
    ads_df[63] = ads_df[13].replace("", "0").astype(str).apply(extract_lead_block) # LEAD 
    ads_df[64] = ads_df[13].replace("", "0").astype(str).apply(extract_ad_block) # AD NAME
    ads_df[65] = ads_df[13].replace("", "0").astype(str).apply(extract_ad_lead) # LEAD + ADNAME
    raw_leads_info_group = ads_df.groupby(63).apply(lambda x: x.values.tolist())
    leads_info_group = deduplicate_leads_group(raw_leads_info_group)
    try:
      generate_daily_report(
        spreadsheet_leads_folder_id=spreadsheet_leads_folder_id,
        leads_info_group=leads_info_group,
        local_date=local_date
      )

      generate_consolidated_report(
        spreadsheet_leads_folder_id=spreadsheet_leads_folder_id,
        leads_info_group=leads_info_group,
        local_date=local_date
      )

    except Exception as e:
      print(f"[ERRO] ao processar {e}")
      
    send_email("Relatórios de Leads - Teste")
    delete_reports_folder()
    return ReportResponse(report_title="Write leads report - Success", generated_at=datetime.now(), message=f"Relatórios de leads escritos com sucesso!", status=200)
  except Exception as e:
    return ReportResponse(report_title="Write leads report - Error", generated_at=datetime.now(), message=f"Error: {str(e)}", status=400)