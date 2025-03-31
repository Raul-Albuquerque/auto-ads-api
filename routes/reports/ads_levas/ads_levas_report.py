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
spreadsheet_active_offers_id="1u8RMIuvGNbsSYSVP_3Tvx0EHJ7sIyU5M"

@router.get("/ads/report/levas")
def write_ads_levas_report():
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
    # return {"data": offer_group}

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
        ads_levas_worksheet_index = search_worksheet_index(active_offer_name, spreadsheet_active_offers_id, "Ads (levas)")
        ads_levas_worksheet = trafic_spreadsheet.get_worksheet(ads_levas_worksheet_index)
        ads_levas_worksheet_data = ads_levas_worksheet.get_all_values()
        print(f"Oferta {active_offer_name} no índice: {ads_levas_worksheet_index}")
        ads_levas_df = pd.DataFrame(ads_levas_worksheet_data)
        ads_levas_df[7] = ads_levas_df[7].astype(str).apply(currency_to_int) # INVESTIDO
        ads_levas_df[8] = ads_levas_df[8].astype(str).apply(currency_to_int) # FATURAMENTO
        ads_levas_df[9] = ads_levas_df[9].astype(str).apply(str_to_int) # VENDAS
        ads_levas_df[14] = ads_levas_df[14].astype(str).apply(str_to_int) # CLICKS
        ads_levas_df[15] = ads_levas_df[15].astype(str).apply(str_to_int) # IMPRESSOES
        ads_levas_df[16] = ads_levas_df[16].astype(str).apply(str_to_int) # VIDEOS VIEWS
        ads_levas_list = ads_levas_df.values.tolist()

        row = 0
        for ad in ads_levas_list:
          row += 1
          if (ad[6] == "⚙️ Testando" or ad[6] == "⏱️ Em validação") and ad[1] in ads_group:
            ad_name = ad[1]
            new_revenue = 0
            new_spend = 0
            new_sales = 0
            new_impressions = 0
            new_link_clicks = 0
            new_video_views = 0

            for sales in sales_ads_group[ad_name]:
              new_sales += sales[0]

            for item in ads_group[ad_name]:
              new_revenue += item[2]
              new_impressions += item[3]
              new_link_clicks += item[4]
              new_spend += item[5]
              new_video_views += item[6]

            if new_spend == 0 and new_revenue == 0:
              continue

            new_ctr = new_link_clicks / new_impressions if new_impressions > 0 else 0
            new_hook_rate = new_video_views / new_impressions if new_impressions > 0 else 0
            new_ctr = round(new_ctr, 4)
            new_hook_rate = round(new_hook_rate, 4)

            ads_levas_current_spend = ad[7]
            ads_levas_current_revenue = ad[8]
            ads_levas_current_sales = ad[9]
            ads_levas_current_clicks = ad[14]
            ads_levas_current_impressions = ad[15]
            ads_levas_current_video_views = ad[16]

            total_spend = ads_levas_current_spend + new_spend if isinstance(ads_levas_current_spend, (int, float)) else ads_levas_current_spend
            total_revenue = ads_levas_current_revenue + new_revenue if isinstance(ads_levas_current_revenue, (int, float)) else ads_levas_current_revenue
            total_sales = ads_levas_current_sales + new_sales if isinstance(ads_levas_current_sales, (int, float)) else ads_levas_current_sales
            total_cpa = int(total_spend / total_sales) if isinstance(total_spend, (int, float)) and isinstance(total_sales, (int, float)) and total_sales > 0 else 0
            total_roas = total_revenue / total_spend if isinstance(total_revenue, int) and isinstance(total_spend, int) and total_spend > 0 else 0
            total_clicks = ads_levas_current_clicks + new_link_clicks if isinstance(ads_levas_current_clicks, (int, float)) else ads_levas_current_clicks
            total_impressions = ads_levas_current_impressions + new_impressions if isinstance(ads_levas_current_impressions, (int, float)) else ads_levas_current_impressions
            total_video_views = ads_levas_current_video_views + new_video_views if isinstance(ads_levas_current_video_views, (int, float)) else ads_levas_current_video_views
            total_hook = total_video_views / total_impressions if isinstance(total_video_views, (int, float)) and isinstance(total_impressions, (int, float)) and total_impressions > 0 else total_video_views
            total_ctr = total_clicks / total_impressions if isinstance(total_clicks, (int, float)) and isinstance(total_impressions, (int, float)) and total_impressions > 0 else total_clicks

            formated_total_spend = int_to_currency(total_spend)
            formated_total_revenue = int_to_currency(total_revenue)
            formated_total_cpa = int_to_currency(total_cpa)
            formated_total_roas = round(total_roas,4)

            ad[7] = total_spend
            ad[8] = total_revenue
            ad[9] = total_sales
            ad[10] = total_cpa
            ad[11] = formated_total_roas
            ad[12] = round(total_hook,4)
            ad[13] = round(total_ctr,4)
            ad[14] = total_clicks
            ad[15] = total_impressions
            ad[16] = total_video_views
            ad[17] = local_time if local_time else ""
            
            folder = "email-reports"
            os.makedirs(folder, exist_ok=True)
            filename = os.path.join(folder, f"{active_offer_name}.txt")
            with open(filename, "a", encoding="utf-8") as file:
              file.write(f"Anúncio: {ad_name} - Na linha: {row}\n")
              file.write(f"Valor Gasto Utmify: {new_spend} - Valor Gasto Ads: {ads_levas_current_spend} - Total: {formated_total_spend}\n")
              file.write(f"Valor Faturado Utmify: {new_revenue} - Valor Faturado Ads: {ads_levas_current_revenue} - Total: {formated_total_revenue}\n")
              file.write(f"Vendas UTMify: {new_sales} - Vendas Ads: {ads_levas_current_sales} - Total: {total_sales}\n")
              file.write(f"Cliques UTMify: {new_link_clicks} - Cliques Ads: {ads_levas_current_clicks} - Total: {total_clicks}\n")
              file.write(f"Impressões UTMify: {new_impressions} - Impressões Ads: {ads_levas_current_impressions} - Total: {total_impressions}\n")
              file.write(f"Videos Views UTMify: {new_video_views} - Videos Views Ads: {ads_levas_current_video_views} - Total: {total_video_views}\n")
              file.write(f"HOOK UTMify: {new_hook_rate} - Total: {round(total_hook, 4)}\n")
              file.write(f"CTR UTMify: {new_ctr} - Total: {round(total_ctr, 4)}\n")
              file.write(f"CPA Total: {formated_total_cpa} - ROAS Total: {formated_total_roas}\n")
              file.write(f"Atualizado em: {local_time}\n")
              file.write("-" * 40 + "\n")

        values_to_write_df = pd.DataFrame(ads_levas_list)
        values_to_write_df[7] = values_to_write_df[7].apply(int_to_currency) # INVESTIDO
        values_to_write_df[8] = values_to_write_df[8].apply(int_to_currency) # FATURAMENTO
        values_to_write_df[10] = values_to_write_df[10].apply(int_to_currency) # CPA
        values_to_write = values_to_write_df.values.tolist()
        # return {"data": offer_group}
        ads_levas_worksheet.clear()
        next_row = 1
        ads_levas_worksheet.update(f"A{next_row}:ZZ{next_row + len(values_to_write) - 1}", values_to_write)
        
    send_email()
    delete_reports_folder()
    return ReportResponse(report_title="Write Ads Levas of all offers - Success", generated_at=datetime.now(), message=f"Relatórios escritos com sucesso!", status=200)
  except Exception as e:
    return ReportResponse(report_title="Write Ads Levas of all offers - Error", generated_at=datetime.now(), message=f"Error: {str(e)}", status=400)