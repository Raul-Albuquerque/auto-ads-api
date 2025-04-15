import pytz, os,csv
from datetime import datetime, timedelta
from fastapi import APIRouter
from itertools import chain
import pandas as pd
import numpy as np

from models.report_models import ReportResponse
from models.active_offers_info import active_offers_info
from core.helpers import delete_reports_folder, groupy_offer
from services.gmail import send_email
from core.cleaners import extract_ad_name, extract_offer_name, extract_ad_d2d_status, extract_ad_d2d_name
from core.numbers_cleaners import currency_to_int, str_to_int, int_to_currency
from services.google_sheets import open_spreadsheet, search_worksheet_index

router = APIRouter()

timezone = pytz.timezone("America/Sao_Paulo")
spreadsheet_db_id="1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz"
spreadsheet_active_offers_id="1z3YUtEjHVH5t5tppLyzSnw972WRbbDcG"

@router.get("/test/ads/d2d/{active_offer_name}")
def write_ads_total_report(active_offer_name:str):
  raw_local_time = datetime.now(timezone) - timedelta(days=1)
  local_date = raw_local_time.strftime("%d/%m/%Y")

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

    print(f"{active_offer_name} teve ocorrencia")
    trafic_spreadsheet = open_spreadsheet(active_offer_name, spreadsheet_active_offers_id)
    ads_d2d_worksheet_index = search_worksheet_index(active_offer_name, spreadsheet_active_offers_id, "Ads Escalados (d2d)")
    ads_d2d_worksheet = trafic_spreadsheet.get_worksheet(ads_d2d_worksheet_index)
      # continue  # Pula para a próxima oferta
    ads_d2d_worksheet_data = ads_d2d_worksheet.get_all_values()
    ads_d2d_group = groupy_offer(ads_d2d_worksheet_data)
    row = 1
    for item in ads_d2d_group:
      raw_ad_name = item[0][0]
      ad_name = extract_ad_d2d_name(raw_ad_name)
      ad_status = extract_ad_d2d_status(raw_ad_name)
      for idx in range(1, len(item[1])):  
        item[1][idx] = currency_to_int(item[1][idx]) 
      for idx in range(1, len(item[2])):  
        item[2][idx] = currency_to_int(item[2][idx])
      for idx in range(1, len(item[3])):  
        item[3][idx] = str_to_int(item[3][idx])
      print(f"{ad_name} com o status: {ad_status}")
      
      item[0].append(local_date)
      if ad_status == "paused":
        item[1].append(0)
        item[2].append(0)
        item[3].append(0)
        item[4].append("")
        item[5].append("")
        row += 6
      else:
        if ad_name in ads_group:
          print(f"o {ad_name} teve resultado ontem")
          new_revenue = 0
          new_spend = 0
          new_sales = 0

          for sales in sales_ads_group[ad_name]:
            new_sales += sales[0]

          for item_ad in ads_group[ad_name]:
            new_revenue += item_ad[2]
            new_spend += item_ad[5]

          new_cpa = int(new_spend / new_sales) if isinstance(new_spend, (int, float)) and isinstance(new_sales, (int, float)) and new_sales > 0 else 0
          new_roas = new_revenue / new_spend if isinstance(new_revenue, int) and isinstance(new_spend, int) and new_spend > 0 else 0
          total_revenue = 0
          total_spend = 0
          total_sales = 0

          item[1].append(new_spend)
          item[2].append(new_revenue)
          item[3].append(new_sales)
          if new_spend > 0:
            item[4].append(new_cpa)
            item[5].append(round(new_roas,4))
          else:
            item[4].append("")
            item[5].append("")
          

          for i in item[1][2:]:
            daily_spend = i if isinstance(i, (int,float)) else 0
            total_spend += daily_spend

          for i in item[2][2:]:
            daily_revenue = i if isinstance(i, (int,float)) else 0
            total_revenue += daily_revenue
          
          for i in item[3][2:]:
            daily_sales = i if isinstance(i, (int,float)) else 0
            total_sales += daily_sales

          total_cpa = int(total_spend / total_sales) if isinstance(total_spend, (int, float)) and isinstance(total_sales, (int, float)) and total_sales > 0 else 0
          total_roas = total_revenue / total_spend if isinstance(total_revenue, int) and isinstance(total_spend, int) and total_spend > 0 else 0

          item[1][1] = total_spend
          item[2][1] = total_revenue
          item[3][1] = total_sales
          item[4][1] = total_cpa
          item[5][1] = round(total_roas,4)

          if new_spend > 0:
            folder = "email-reports"
            os.makedirs(folder, exist_ok=True)
            filename = os.path.join(folder, f"{active_offer_name}-d2d.txt")
            with open(filename, "a", encoding="utf-8") as file:
              file.write(f"Anúncio: {ad_name} - Na linha: {row}\n")
              file.write(f"Valor Gasto Utmify: {new_spend} - Gasto Total: {int_to_currency(total_spend)}\n")
              file.write(f"Valor Faturado Utmify: {new_revenue} - Faturamento Total: {int_to_currency(total_revenue)}\n")
              file.write(f"Vendas UTMify: {new_sales} - Vendas Totais: {total_sales}\n")
              file.write(f"Total CPA: {new_cpa} - Total CPA: {int_to_currency(total_cpa)}\n")
              file.write(f"Total ROAS: {round(new_roas,4)} - Total ROAS: {round(total_roas,4)}\n")
              file.write(f"Atualizado em: {local_date}\n")
              file.write("-" * 40 + "\n")
          row += 6

        else:
          item[1].append(0)
          item[2].append(0)
          item[3].append(0)
          item[4].append("")
          item[5].append("")
          row += 6

    for bloco in ads_d2d_group:
      investimento = bloco[1]
      faturamento = bloco[2]
      cpa = bloco[4] 
      for idx in range(1, len(investimento)):
        investimento[idx] = int_to_currency(investimento[idx])
      for idx in range(1, len(faturamento)):
        faturamento[idx] = int_to_currency(faturamento[idx])
      for idx in range(1, len(cpa)):
        cpa[idx] = int_to_currency(cpa[idx])
    # return ads_d2d_group
    data_to_write = list(chain(*ads_d2d_group))
    # return{"data": data_to_write}
    ads_d2d_worksheet.clear()
    next_row = 1
    ads_d2d_worksheet.update(f"A{next_row}:ZZ{next_row + len(data_to_write) - 1}", data_to_write)
    send_email("Relatórios de Ads D2D - Teste")
    delete_reports_folder()
    return ReportResponse(report_title="Write Ads D2D Report - Success", generated_at=datetime.now(), message=f"Ads D2D was written successfully!", status=200)

  except Exception as e:
    return ReportResponse(report_title="Write Ads D2D Report - Error", generated_at=datetime.now(), message=f"Error: {str(e)}", status=400)