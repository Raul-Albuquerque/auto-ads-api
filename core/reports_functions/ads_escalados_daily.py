import os
from datetime import datetime

from models.report_models import ReportResponse
from models.active_offers_info import active_offers_info
from core.helpers import groupy_leads, ungroup_leads
from core.numbers_cleaners import currency_to_int, str_to_int, int_to_currency
from services.google_sheets import open_spreadsheet, search_worksheet_index, duplicate_template_sheet_to_end

# active_offer = "LVH_ESP"

def generate_ads_escalados_daily_report(spreadsheet_escalados_folder_id: str, ads_group: any, local_date: str, local_time: str):
  for active_offer_item in active_offers_info:
    active_offer = active_offer_item['offer_name']
    try:
      ads_escalados_spreadsheet = open_spreadsheet(active_offer, spreadsheet_escalados_folder_id)
      ads_escalados_worksheet_index = search_worksheet_index(active_offer, spreadsheet_escalados_folder_id, "MODELO")
      ads_escalados = ads_escalados_spreadsheet.get_worksheet(ads_escalados_worksheet_index).get_all_values()
    except Exception as e:
      error_msg = f"Erro ao abrir a planilha {active_offer}: {e}"
      print(error_msg)
      continue

    ads_escalados_to_write_index = search_worksheet_index(active_offer, spreadsheet_escalados_folder_id, local_date)
    is_ads_escalados_date_table_exists = True if ads_escalados_to_write_index else False
    ads_escalados_current_data = ads_escalados_spreadsheet.get_worksheet(ads_escalados_to_write_index).get_all_values() if is_ads_escalados_date_table_exists else None
    if ads_escalados_current_data:
      ads_current_info = [ads for ads in ads_escalados_current_data[1:-1]]
      for ad_current_info in ads_current_info:
        ad_current_info[0] = "ADV+" if ad_current_info[0] == "CAMPANHAS ADV+ - TOP Ads" else active_offer if ad_current_info[0] == "TESTE DE VALIDAÇÃO DE CRIATIVO" else ad_current_info[0]
        ad_current_info[3] = currency_to_int(ad_current_info[3])
      ads_current_info_dict = {linha[0]: linha[3] for linha in ads_current_info}

    for ad in ads_escalados[1:-1]:
      ad_name = "ADV+" if ad[0] == "CAMPANHAS ADV+ - TOP Ads" else active_offer if ad[0] == "TESTE DE VALIDAÇÃO DE CRIATIVO" else ad[0]
      current_budget = ads_current_info_dict[ad_name] if ads_escalados_current_data else 0
      new_sales = 0 
      new_spend = 0
      new_revenue = 0
      new_cpa = 0
      new_roas = 0
      if ad_name in ads_group:        
        new_sales = sum([spend[1] for spend in ads_group[ad_name]])
        new_revenue = sum([spend[4] for spend in ads_group[ad_name]])
        new_spend = sum([spend[5] for spend in ads_group[ad_name]])
        new_cpa = int(new_spend / new_sales) if new_sales > 0 else 0
        new_roas = round(new_revenue / new_spend if new_revenue > 0 and new_spend > 0 else 0, 2)
        folder = "email-reports"
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, f"{active_offer}_ads_escalados_daily.txt")
        with open(filename, "a", encoding="utf-8") as file:
          file.write(f"O anúncio: {ad_name} - no dia: {local_date}\n")
          file.write(f"Gastou: {new_spend}\n")
          file.write(f"Faturou: {new_revenue} - Vendeu: {new_sales}\n")
          file.write(f"CPA: {new_cpa} - ROAS: {new_roas}\n")
          file.write("-" * 40 + "\n")
      new_ad_name = "CAMPANHAS ADV+ - TOP Ads" if ad_name == "ADV+" else "TESTE DE VALIDAÇÃO DE CRIATIVO" if ad_name == active_offer else ad_name
      ad[0] = new_ad_name
      ad[3] = current_budget
      ad[4] = new_spend
      ad[5] = new_revenue
      ad[6] = new_sales
      ad[7] = new_cpa
      ad[8] = new_roas
      ad[9] = local_time

    total_budget = sum([i[3] for i in ads_escalados[1:-1]])
    total_spend = sum([i[4] for i in ads_escalados[1:-1]])
    total_revenue = sum([i[5] for i in ads_escalados[1:-1]])
    total_sales = sum([i[6] for i in ads_escalados[1:-1]])
    total_cpa = int(total_spend / total_sales) if total_sales > 0 else 0
    total_roas = round(total_revenue / total_spend if total_revenue > 0 and total_spend > 0 else 0, 2)
    ads_escalados[-1] = ["AGREGADO","","",int_to_currency(total_budget), int_to_currency(total_spend), int_to_currency(total_revenue), total_sales, int_to_currency(total_cpa), total_roas,local_time]
    for formatted_ads in ads_escalados[1:-1]:
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
    
    next_row = 1
    ads_escalados_to_write.update(f"A{next_row}:ZZ{next_row + len(ads_escalados) - 1}", ads_escalados)      
  return ReportResponse(report_title="Daily Ads Escalados Report - Success", generated_at=datetime.now(), message=f"Relatório de Ads Escalados escrito com sucesso!", status=200)