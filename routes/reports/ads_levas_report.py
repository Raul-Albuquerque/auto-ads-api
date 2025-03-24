import pytz
from datetime import datetime
from fastapi import APIRouter
import pandas as pd

from models.report_models import ReportResponse
from core.helpers import get_average_rate
from core.cleaners import extract_ad_name, extract_offer_name
from core.numbers_cleaners import currency_to_int, str_to_int, percentage_to_float, percentage_to_float_from_utmify_hook, percentage_to_float_from_utmify_ctr, int_to_currency
from services.google_sheets import open_spreadsheet, search_worksheet_index

router = APIRouter()

timezone = pytz.timezone("America/Sao_Paulo")
raw_local_time = datetime.now(timezone)
local_time = raw_local_time.strftime("%d/%m/%Y-%H:%M:%S")

@router.get("/ads/report/levas")
def get_all_ads():

  try:
    ads_spreadsheet = open_spreadsheet("DB_3.0", "1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz")
    ads_worksheet_index = search_worksheet_index("DB_3.0", "1kYakvWtJ-2G1Vu-ylxb4qYCzSoozMunz", "RAW2")
    ads_worksheet = ads_spreadsheet.get_worksheet(ads_worksheet_index)
    ads = ads_worksheet.get_all_values()
    ads_df = pd.DataFrame(ads)
    ads_df = ads_df.drop(ads_df.columns[[0,1,2,3,4,5,6,7,8,10,11,12,14,15,16,17,19,20,21,22,23,24,26,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,48,49,50,51,52,53,54,55,56,57,58,59,60,61]], axis=1)
    ads_df[9] = ads_df[9].astype(str).apply(str_to_int) # SALES
    ads_df[18] = ads_df[18].astype(str).apply(str_to_int) # REVENUE
    ads_df[27] = ads_df[27].astype(str).apply(str_to_int) # SPEND
    ads_df[47] = ads_df[47].astype(str).apply(percentage_to_float_from_utmify_hook) # HOOK
    ads_df[25] = ads_df[25].astype(str).apply(percentage_to_float_from_utmify_ctr) # CTR
    ads_df[62] = ads_df[13].astype(str).apply(extract_ad_name) # AD NAME
    ads_df[63] = ads_df[13].astype(str).apply(extract_offer_name) # OFFER
    ads_group = ads_df.groupby(62).apply(lambda x: x.values.tolist())

    trafic_spreadsheet = open_spreadsheet("LVH_ESP", "1XV7_jD-QLxEvQe695iwX-_-7ruDYJGQQ")
    ads_levas_worksheet_index = search_worksheet_index("LVH_ESP", "1XV7_jD-QLxEvQe695iwX-_-7ruDYJGQQ", "Ads (levas)")
    ads_levas_worksheet = trafic_spreadsheet.get_worksheet(ads_levas_worksheet_index)
    ads_levas_worksheet_data = ads_levas_worksheet.get_all_values()
    ads_levas_df = pd.DataFrame(ads_levas_worksheet_data)
    ads_levas_df[7] = ads_levas_df[7].astype(str).apply(currency_to_int) # INVESTIDO
    ads_levas_df[8] = ads_levas_df[8].astype(str).apply(currency_to_int) # FATURAMENTO
    ads_levas_df[9] = ads_levas_df[9].astype(str).apply(str_to_int) # VENDAS
    ads_levas_df[12] = ads_levas_df[12].astype(str).apply(percentage_to_float) # HOOK
    ads_levas_df[13] = ads_levas_df[13].astype(str).apply(percentage_to_float) # CTR
    ads_levas_list = ads_levas_df.values.tolist()

    for ad in ads_levas_list:
      if (ad[6] == "⚙️ Testando" or ad[6] == "⏱️ Em validação") and ad[1] in ads_group:
        ad_name = ad[1]
        new_revenue = 0
        new_spend = 0
        new_sales = 0
        ctr_values = []
        hook_rate_values = []

        for item in ads_group[ad_name]:
          new_revenue += item[2]
          new_spend += item[4]
          new_sales += item[0]  

          if item[3] != 0:
            ctr_values.append(item[3])
          
          if item[5] != 0:
            hook_rate_values.append(item[5])

        new_ctr = sum(ctr_values) / len(ctr_values) if ctr_values else 0
        new_hook_rate = sum(hook_rate_values) / len(hook_rate_values) if hook_rate_values else 0
        new_ctr = round(new_ctr, 4)
        new_hook_rate = round(new_hook_rate, 4)

        ads_levas_current_spend = ad[7]
        ads_levas_current_revenue = ad[8]
        ads_levas_current_sales = ad[9]
        ads_levas_current_hook = ad[12]
        ads_levas_current_ctr = ad[13]

        total_spend = ads_levas_current_spend + new_spend if isinstance(ads_levas_current_spend, (int, float)) else ads_levas_current_spend
        total_revenue = ads_levas_current_revenue + new_revenue if isinstance(ads_levas_current_revenue, (int, float)) else ads_levas_current_revenue
        total_sales = ads_levas_current_sales + new_sales if isinstance(ads_levas_current_sales, (int, float)) else ads_levas_current_sales
        total_cpa = int(total_spend / total_sales) if isinstance(total_spend, (int, float)) and isinstance(total_sales, (int, float)) and total_sales > 0 else 0
        total_roas = (total_revenue * 100) // total_spend if isinstance(total_revenue, int) and isinstance(total_spend, int) and total_spend > 0 else 0
        total_hook = get_average_rate(new_rate=new_hook_rate, current_rate=ads_levas_current_hook)
        total_ctr = get_average_rate(new_rate=new_ctr, current_rate=ads_levas_current_ctr)

        formated_total_spend = int_to_currency(total_spend)
        formated_total_revenue = int_to_currency(total_revenue)
        formated_total_cpa = int_to_currency(total_cpa)
        formated_total_roas = int_to_currency(total_roas)
        formated_total_hook = round(total_hook * 100, 2)
        formated_total_ctr = round(total_ctr * 100, 2)

        ad[7] = formated_total_spend
        ad[8] = formated_total_revenue
        ad[9] = total_sales
        ad[10] = formated_total_cpa
        ad[11] = formated_total_roas
        ad[12] = formated_total_hook
        ad[13] = formated_total_ctr
        ad[14] = local_time

        # Exibindo os resultados
        print(f"Anúncio: {ad_name}")
        print(f"Valor Gasto Utmify: {new_spend} - Valor Gasto Ads: {ads_levas_current_spend} - Total: {formated_total_spend}")
        print(f"Valor Faturado Utmify: {new_revenue} - Valor Faturado Ads: {ads_levas_current_revenue} - Total: {formated_total_revenue}")
        print(f"Vendas UTMify: {new_sales} - Vendas Ads: {ads_levas_current_sales} - Total: {total_sales}")
        print(f"HOOK UTMify: {new_hook_rate} - HOOK Ads: {ads_levas_current_hook} - Total: {formated_total_hook}")
        print(f"CTR UTMify: {new_ctr} - CTR Ads: {ads_levas_current_ctr} - Total: {formated_total_ctr}")
        print(f"CPA Total: {formated_total_cpa} - ROAS Total: {formated_total_roas}")
        print(f"Atualizado em: {local_time}")
        print("-" * 40)

    return {"data": ads_levas_list}
    


  except Exception as e:
    return ReportResponse(report_title="Get All Purchases", generated_at=datetime.now(), data={"Error": str(e)})