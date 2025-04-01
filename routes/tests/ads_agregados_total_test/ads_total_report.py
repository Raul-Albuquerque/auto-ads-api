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

@router.get("/test/ads/total")
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
    # return {"data": ads_group}

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

    for item in active_offers_info:
      active_offer_name = item["offer_name"]
      if active_offer_name in offer_group:
        print(f"{active_offer_name} teve ocorrencia")
        try:
          trafic_spreadsheet = open_spreadsheet(active_offer_name, spreadsheet_active_offers_id)
        except Exception as e:
          print(f"Erro ao abrir a planilha {active_offer_name}: {e}")
          continue  # Pula para a próxima oferta
        ads_total_worksheet_index = search_worksheet_index(active_offer_name, spreadsheet_active_offers_id, "Ads Escalados (Agreg.)")
        ads_total_worksheet = trafic_spreadsheet.get_worksheet(ads_total_worksheet_index)
        ads_total_worksheet_data = ads_total_worksheet.get_all_values()
        print(f"Oferta {active_offer_name} no índice: {ads_total_worksheet_index}")
        ads_total_df = pd.DataFrame(ads_total_worksheet_data)
        ads_total_df[2] = ads_total_df[2].astype(str).apply(currency_to_int) # INVESTIDO
        ads_total_df[3] = ads_total_df[3].astype(str).apply(currency_to_int) # FATURAMENTO
        ads_total_df[6] = ads_total_df[6].astype(str).apply(str_to_int) # vendas
        ads_total_list = ads_total_df.values.tolist()
        # return {"ads": ads_group}
        row = 0
        for ad in ads_total_list:
          row += 1
          ad_name = ad[0]
          
          if ad_name == "" or ad[1] == "😞 Saturou" or ad[1] == "" or ad_name not in ads_group:
            continue

          if ad_name in ads_group:
            new_revenue = 0
            new_spend = 0
            new_sales = 0

            for sales in sales_ads_group[ad_name]:
              new_sales += sales[0]

            for item_ad in ads_group[ad_name]:
              new_revenue += item_ad[2]
              new_spend += item_ad[5]
            
            if new_spend == 0:
              continue

            ads_total_current_spend = ad[2]
            ads_total_current_revenue = ad[3]
            ads_total_current_sales = ad[6]

            total_spend = ads_total_current_spend + new_spend if isinstance(ads_total_current_spend, (int, float)) else ads_total_current_spend
            total_revenue = ads_total_current_revenue + new_revenue if isinstance(ads_total_current_revenue, (int, float)) else ads_total_current_revenue
            total_sales = ads_total_current_sales + new_sales if isinstance(ads_total_current_sales, (int, float)) else ads_total_current_sales
            total_cpa = int(total_spend / total_sales) if isinstance(total_spend, (int, float)) and isinstance(total_sales, (int, float)) and total_sales > 0 else 0
            total_roas = total_revenue / total_spend if isinstance(total_revenue, int) and isinstance(total_spend, int) and total_spend > 0 else 0
            formatted_total_roas = round(total_roas,4)
            formatted_total_cpa = int_to_currency(total_cpa)

            ad[2] = total_spend
            ad[3] = total_revenue
            ad[4] = formatted_total_roas
            ad[5] = total_cpa
            ad[6] = total_sales
            ad[7] = local_time if local_time else ""

            folder = "email-reports"
            os.makedirs(folder, exist_ok=True)
            filename = os.path.join(folder, f"{active_offer_name}.txt")
            with open(filename, "a", encoding="utf-8") as file:
              file.write(f"Anúncio: {ad_name} - Na linha: {row}\n")
              file.write(f"Valor Gasto Utmify: {new_spend} - Valor Gasto Ads: {ads_total_current_spend} - Total: {total_spend}\n")
              file.write(f"Valor Faturado Utmify: {new_revenue} - Valor Faturado Ads: {ads_total_current_revenue} - Total: {total_revenue}\n")
              file.write(f"Vendas UTMify: {new_sales} - Vendas Ads: {ads_total_current_sales} - Total: {total_sales}\n")
              file.write(f"CPA Total: {formatted_total_cpa} - ROAS Total: {formatted_total_roas}\n")
              file.write(f"Atualizado em: {local_time}\n")
              file.write("-" * 40 + "\n")
        
        values_to_write_df = pd.DataFrame(ads_total_list)
        values_to_write_df[2] =  values_to_write_df[2].apply(int_to_currency) #GASTO
        values_to_write_df[3] =  values_to_write_df[3].apply(int_to_currency) #FATURAMENTO
        values_to_write_df[5] = values_to_write_df[5].apply(int_to_currency) # CPA
        values_to_write = values_to_write_df.values.tolist()
        ads_total_worksheet.clear()
        next_row = 1
        ads_total_worksheet.update(f"A{next_row}:ZZ{next_row + len(values_to_write) - 1}", values_to_write)
    
    send_email("Relatórios de Ads Total - teste")
    delete_reports_folder()
    return ReportResponse(report_title="Write Ads Total Report - Success", generated_at=datetime.now(), message=f"Ads Total was written successfully!", status=200)

  except Exception as e:
    return ReportResponse(report_title="Write Ads Total of all offers - Error", generated_at=datetime.now(), message=f"Error: {str(e)}", status=400)