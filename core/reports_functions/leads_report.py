import os
from datetime import datetime

from models.report_models import ReportResponse
from models.active_offers_info import active_offers_info
from core.helpers import groupy_leads, ungroup_leads
from core.numbers_cleaners import currency_to_int, str_to_int, int_to_currency
from services.google_sheets import open_spreadsheet, search_worksheet_index, duplicate_template_sheet_to_end

def generate_daily_report(spreadsheet_leads_folder_id: str, leads_info_group: any, local_date):
  for active_offer_item in active_offers_info:
    active_offer = active_offer_item['offer_name']
    try:
      leads_spreadsheet = open_spreadsheet(active_offer, spreadsheet_leads_folder_id)
      leads_worksheet_index = search_worksheet_index(active_offer, spreadsheet_leads_folder_id, "Modelo")
      leads_worksheet = leads_spreadsheet.get_worksheet(leads_worksheet_index)
    except Exception as e:
      error_msg = f"Erro ao abrir a planilha {active_offer}: {e}"
      print(error_msg)
      continue
    all_leads = leads_worksheet.get_all_values()
    leads_group = groupy_leads(all_leads)

    for lead in leads_group:
      lead_name = lead[1][1]
      if lead_name in leads_info_group:
        print(f"a {lead_name} teve ocorrência na lista")
        print('_' * 50)
        new_sales_amount = 0
        new_spend_amount = 0
        new_revenue_amount = 0
        for ad in lead[7:]:
          ad_name = ad[1]
          ad[2] = currency_to_int(ad[2]) # spend
          ad[3] = currency_to_int(ad[3]) # revenue
          ad[4] = str_to_int(ad[4]) # sales
          new_sales = 0
          new_spend = 0
          new_revenue = 0
          new_cpa = 0
          new_roas = 0
          new_arpu = 0
          if ad_name in leads_info_group[lead_name]:
            new_sales = leads_info_group[lead_name][ad_name][1]
            new_revenue = leads_info_group[lead_name][ad_name][3]
            new_spend = leads_info_group[lead_name][ad_name][4]
            new_cpa = int(new_spend / new_sales) if new_sales > 0 else 0
            new_roas = new_revenue / new_spend if new_revenue > 0 and new_spend > 0 else 0
            new_arpu = int(new_revenue / new_sales) if new_sales > 0 else 0

            folder = "email-reports"
            os.makedirs(folder, exist_ok=True)
            filename = os.path.join(folder, f"{active_offer}_LEADS_DAILY.txt")
            with open(filename, "a", encoding="utf-8") as file:
              file.write(f"O anúncio: {ad_name} - na Lead: {lead_name}\n")
              file.write(f"Gastos UTMify: {new_spend}\n")
              file.write(f"Faturamento UTMify: {new_revenue}\n")
              file.write(f"Vendas UTMIfy: {new_sales}\n")
              file.write(f"Novo CPA: {new_cpa} - Novo ROAS: {round(new_roas,4)} - Novo ARPU: {new_arpu}\n")
              file.write("-" * 40 + "\n")
          
          ad[2] = int_to_currency(new_spend)
          ad[3] = int_to_currency(new_revenue)
          ad[4] = new_sales 
          ad[5] = int_to_currency(new_cpa)
          ad[6] = round(new_roas,4)
          ad[7] = int_to_currency(new_arpu)

        new_spend_amount = sum([item[2] for item in lead[7:]])
        new_revenue_amount = sum([item[3] for item in lead[7:]])
        new_sales_amount = sum([item[4] for item in lead[7:]])
        new_cpa_amount = int(new_spend_amount / new_sales_amount) if new_sales_amount > 0 else 0
        new_roas_amount = new_revenue_amount / new_spend_amount if new_revenue_amount > 0 and new_spend_amount > 0 else 0
        new_arpu_amount = int(new_revenue_amount / new_sales_amount) if new_sales_amount > 0 else 0
        lead[4][:] = ["","",int_to_currency(new_spend_amount * 100),int_to_currency(new_revenue_amount * 100),new_sales_amount,new_cpa_amount,round(new_roas_amount,4),int_to_currency(new_arpu_amount)]

    daily_lead_info = ungroup_leads(leads_group)
    daily_lead_worksheet_index = search_worksheet_index(active_offer, spreadsheet_leads_folder_id, local_date)
    if daily_lead_worksheet_index:
      daily_lead_worksheet = leads_spreadsheet.get_worksheet(daily_lead_worksheet_index)
      daily_lead_worksheet.clear()
    else:
      daily_lead_worksheet = duplicate_template_sheet_to_end(
        spreadsheet=leads_spreadsheet,
        template_sheet_index=leads_worksheet_index,
        new_sheet_name=local_date
      )
      daily_lead_worksheet.clear()
    next_row = 1
    daily_lead_worksheet.update(f"A{next_row}:ZZ{next_row + len(daily_lead_info) - 1}", daily_lead_info)
  return ReportResponse(report_title="Daily Leads report function - Success", generated_at=datetime.now(), message=f"Função executada com sucesso!", status=200)

def generate_consolidated_report(spreadsheet_leads_folder_id: str, leads_info_group: any, local_date):
  for active_offer_item in active_offers_info:
    active_offer = active_offer_item['offer_name']
    try:
      leads_spreadsheet = open_spreadsheet(active_offer, spreadsheet_leads_folder_id)
      leads_worksheet_index = search_worksheet_index(active_offer, spreadsheet_leads_folder_id, "Modelo")
      leads_worksheet = leads_spreadsheet.get_worksheet(leads_worksheet_index)
    except Exception as e:
      error_msg = f"Erro ao abrir a planilha {active_offer}: {e}"
      print(error_msg)
      continue
    all_leads = leads_worksheet.get_all_values()
    leads_group = groupy_leads(all_leads)

    for lead in leads_group:
      lead_name = lead[1][1]
      if lead_name in leads_info_group:
        print(f"a {lead_name} teve ocorrência na lista")
        print('_' * 50)
        new_sales_amount = 0
        new_spend_amount = 0
        new_revenue_amount = 0
        for ad in lead[7:]:
          ad_name = ad[1]
          ad[2] = currency_to_int(ad[2]) # spend
          ad[3] = currency_to_int(ad[3]) # revenue
          ad[4] = str_to_int(ad[4]) # sales
          current_spend = ad[2]
          current_revenue = ad[3]
          current_sales = ad[4]
          new_sales = 0
          new_spend = 0
          new_revenue = 0
          new_cpa = 0
          new_roas = 0
          new_arpu = 0
          total_spend = 0
          total_revenue = 0
          total_sales = 0
          total_cpa = 0
          total_roas = 0
          total_arpu = 0
          if ad_name in leads_info_group[lead_name]:
            new_sales = leads_info_group[lead_name][ad_name][1]
            new_revenue = leads_info_group[lead_name][ad_name][3]
            new_spend = leads_info_group[lead_name][ad_name][4]
            new_cpa = int(new_spend / new_sales) if new_sales > 0 else 0
            new_roas = new_revenue / new_spend if new_revenue > 0 and new_spend > 0 else 0
            new_arpu = int(new_revenue / new_sales) if new_sales > 0 else 0
            total_spend = current_spend + new_spend
            total_revenue = current_revenue + new_revenue
            total_sales = current_sales + new_sales
            total_cpa = int(total_spend / total_sales) if total_sales > 0 else 0
            total_roas = total_revenue / total_spend if total_revenue > 0 and total_spend > 0 else 0
            total_arpu = int(total_revenue / total_sales) if total_sales > 0 else 0

            folder = "email-reports"
            os.makedirs(folder, exist_ok=True)
            filename = os.path.join(folder, f"{active_offer}_LEADS_AGGREGATED.txt")
            with open(filename, "a", encoding="utf-8") as file:
              file.write(f"O anúncio: {ad_name} - na Lead: {lead_name}\n")
              file.write(f"Gastos Atual: {current_spend} - Gastos UTMify: {new_spend} - Gasto Total: {total_spend}\n")
              file.write(f"Faturamento atual: {current_revenue} - faturamento UTMify: {new_revenue} - Faturamento Total: {total_revenue}\n")
              file.write(f"Vendas atuais: {current_sales} - Vendas UTMIfy: {new_sales} - Vendas total: {total_sales}\n")
              file.write(f"Novo CPA: {new_cpa} - Novo ROAS: {round(new_roas,4)} - Novo ARPU: {new_arpu}\n")
              file.write(f"Total CPA: {total_cpa} - Total ROAS: {round(total_roas,4)} - Total ARPU: {total_arpu}\n")
              file.write("-" * 40 + "\n")
          
          ad[2] = int_to_currency(total_spend)
          ad[3] = int_to_currency(total_revenue)
          ad[4] = total_sales 
          ad[5] = int_to_currency(total_cpa)
          ad[6] = round(total_roas,4)
          ad[7] = int_to_currency(total_arpu)

        new_spend_amount = sum([item[2] for item in lead[7:]])
        new_revenue_amount = sum([item[3] for item in lead[7:]])
        new_sales_amount = sum([item[4] for item in lead[7:]])
        new_cpa_amount = int(new_spend_amount / new_sales_amount) if new_sales_amount > 0 else 0
        new_roas_amount = new_revenue_amount / new_spend_amount if new_revenue_amount > 0 and new_spend_amount > 0 else 0
        new_arpu_amount = int(new_revenue_amount / new_sales_amount) if new_sales_amount > 0 else 0
        lead[4][:] = ["","",int_to_currency(new_spend_amount * 100),int_to_currency(new_revenue_amount * 100),new_sales_amount,new_cpa_amount,round(new_roas_amount,4),int_to_currency(new_arpu_amount)]

    daily_lead_info = ungroup_leads(leads_group)
    next_row = 1
    leads_worksheet.update(f"A{next_row}:ZZ{next_row + len(daily_lead_info) - 1}", daily_lead_info)
  return ReportResponse(report_title="Agreggated Leads report function - Success", generated_at=datetime.now(), message=f"Função executada com sucesso!", status=200)