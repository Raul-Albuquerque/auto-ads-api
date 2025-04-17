import os
from datetime import datetime

from models.report_models import ReportResponse
from models.active_offers_info import active_offers_info
from core.helpers import groupy_leads, ungroup_leads
from core.numbers_cleaners import currency_to_int, str_to_int, int_to_currency
from services.google_sheets import open_spreadsheet, search_worksheet_index, duplicate_template_sheet_to_end

active_offer = "LVH_ESP"

def generate_ads_escalados_daily_report(spreadsheet_escalados_folder_id: str, ads_group: any, local_date: str, local_time: str):
  try:
    ads_escalados_spreadsheet = open_spreadsheet(active_offer, spreadsheet_escalados_folder_id)
    ads_escalados_worksheet_index = search_worksheet_index(active_offer, spreadsheet_escalados_folder_id, "MODELO")
    ads_escalados = ads_escalados_spreadsheet.get_worksheet(ads_escalados_worksheet_index).get_all_values()
  except Exception as e:
    error_msg = f"Erro ao abrir a planilha {active_offer}: {e}"
    print(error_msg)

  for ad in ads_escalados[1:-3]:
    ad_name = "ADV+" if ad[0] == "CAMPANHAS ADV+ - TOP Ads" else ad[0]
    new_daily_budget = 0 
    new_sales = 0 
    new_spend = 0
    new_revenue = 0
    if ad_name in ads_group:        
      new_sales = sum([spend[1] for spend in ads_group[ad_name]])
      new_daily_budget = sum([spend[3] for spend in ads_group[ad_name]])
      new_revenue = sum([spend[4] for spend in ads_group[ad_name]])
      new_spend = sum([spend[5] for spend in ads_group[ad_name]])
      new_cpa = int(new_spend / new_sales) if new_sales > 0 else 0
      new_roas = round(new_revenue / new_spend if new_revenue > 0 and new_spend > 0 else 0, 4)
      folder = "email-reports"
      os.makedirs(folder, exist_ok=True)
      filename = os.path.join(folder, f"{active_offer}_ads_escalados_daily.txt")
      with open(filename, "a", encoding="utf-8") as file:
        file.write(f"O anúncio: {ad_name} - no dia: {local_date}\n")
        file.write(f"Gastou: {new_spend} - Budget: {new_daily_budget}\n")
        file.write(f"Faturou: {new_revenue} - Vendeu: {new_sales}\n")
        file.write(f"CPA: {new_cpa} - ROAS: {new_roas}\n")
        file.write("-" * 40 + "\n")
    new_ad_name = "CAMPANHAS ADV+ - TOP Ads+" if ad_name == "ADV+" else ad_name
    ad[0] = new_ad_name
    ad[3] = new_daily_budget
    ad[4] = new_spend
    ad[5] = new_revenue
    ad[6] = new_sales
    ad[7] = new_cpa
    ad[8] = new_roas
    ad[9] = local_time
  
  total_budget = sum([i[3] for i in ads_escalados[1:-3]])
  total_spend = sum([i[4] for i in ads_escalados[1:-3]])
  total_revenue = sum([i[5] for i in ads_escalados[1:-3]])
  total_sales = sum([i[6] for i in ads_escalados[1:-3]])
  total_cpa = int(total_spend / total_sales) if total_sales > 0 else 0
  total_roas = round(total_revenue / total_spend if total_revenue > 0 and total_spend > 0 else 0, 4)
  ads_escalados[-1] = ["AGREGADO","","",int_to_currency(total_budget), int_to_currency(total_spend), int_to_currency(total_revenue), total_sales, int_to_currency(total_cpa), total_roas,local_time]
  for formatted_ads in ads_escalados[1:-3]:
    formatted_ads[3] = int_to_currency(formatted_ads[3])
    formatted_ads[4] = int_to_currency(formatted_ads[4])
    formatted_ads[5] = int_to_currency(formatted_ads[5])
    formatted_ads[7] = int_to_currency(formatted_ads[7])
  ads_escalados_to_write_index = search_worksheet_index(active_offer, spreadsheet_escalados_folder_id, local_date)
  if ads_escalados_to_write_index:
    ads_escalados_to_write = ads_escalados_spreadsheet.get_worksheet(ads_escalados_to_write_index)
    ads_escalados_to_write.clear()
  else:
    ads_escalados_to_write = duplicate_template_sheet_to_end(
      spreadsheet=ads_escalados_spreadsheet,
      template_sheet_index=ads_escalados_worksheet_index,
      new_sheet_name=local_date
    )
    ads_escalados_to_write.clear()
  next_row = 1
  ads_escalados_to_write.update(f"A{next_row}:ZZ{next_row + len(ads_escalados) - 1}", ads_escalados)
  return ReportResponse(report_title="Daily Ads Escalados Report - Success", generated_at=datetime.now(), message=f"Função executada com sucesso!", status=200)