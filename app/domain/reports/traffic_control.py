import os
from datetime import datetime, timedelta
import pandas as pd

from app.models.report_model import ReportResponse
from app.external_services.google_sheets import open_spreadsheet, search_worksheet_index
from app.core.cleaners import extract_offer_name
from app.core.numbers_manipulators import str_to_int, currency_to_int, extract_int
from config import (
    DB_SPREADSHEET,
    DB_SPREADSHEET_FOLDER_ID,
    REPORT_TYPE_DATA_WORKSHEETS,
    REPORT_TYPE_FRONT_SALES_WORKSHEETS,
)


# VAI CONSULTAR A TABELA DO VTURB E RETORNAR OS DADOS
async def get_vturb_info(ad_plataform: str):
    try:
        player_stats_spreadsheet = open_spreadsheet(
            DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID
        )
        player_stats_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_DATA_WORKSHEETS["vturb"],
        )
        player_stats_worksheet = player_stats_spreadsheet.get_worksheet(
            player_stats_worksheet_index
        )
        player_stats = player_stats_worksheet.get_all_values()
        return player_stats

    # FALTA CONVERTER PARA DATAFRAME AGLUTINAR OS DADOS POR OFERTAS E PLATAFORMA E DEPOIS RETORNAR O DICT
    except Exception as e:
        return ReportResponse(
            report_title="Get Vturb Info - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )


async def get_yt_ads_info(ad_plataform: str):
    try:
        yt_ads_sales_spreadsheet = open_spreadsheet(
            DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID
        )
        yt_ads_sales_spreadsheet_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_FRONT_SALES_WORKSHEETS[ad_plataform],
        )
        yt_ads_sales_spreadsheet_worksheet = yt_ads_sales_spreadsheet.get_worksheet(
            yt_ads_sales_spreadsheet_worksheet_index
        )
        yt_ads_sales = yt_ads_sales_spreadsheet_worksheet.get_all_values()
        yt_ads_sales_df = pd.DataFrame(yt_ads_sales)
        # fmt: off
        yt_ads_sales_df = yt_ads_sales_df.drop(yt_ads_sales_df.columns[[0,1,2,3,4,5,6,7,8,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38]], axis=1)
        # fmt: on
        yt_sales_ads_list = yt_ads_sales_df.groupby(11).apply(
            lambda x: x.values.tolist()
        )
        yt_ads_spreadsheet = open_spreadsheet(DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID)
        yt_ads_spreadsheet_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_DATA_WORKSHEETS[ad_plataform],
        )
        yt_ads_spreadsheet_worksheet = yt_ads_spreadsheet.get_worksheet(
            yt_ads_spreadsheet_worksheet_index
        )
        yt_ads = yt_ads_spreadsheet_worksheet.get_all_values()
        for yt_ad in yt_ads[1:]:
            yt_ad_id = yt_ad[11]
            yt_ad[9] = yt_sales_ads_list[yt_ad_id][0][0]
        yt_ads_df = pd.DataFrame(yt_ads)
        # fmt: off
        yt_ads_df = yt_ads_df.drop(yt_ads_df.columns[[0,1,2,3,4,5,6,7,8,10,13,14,15,16,17,18,19,21,22,23,24,25,27,28,31,32,33,34,35,36,37,38]], axis=1)
        # fmt: on
        yt_ads_df[13] = (
            yt_ads_df[12].replace("", "0").astype(str).apply(extract_offer_name)
        )
        yt_ads_df[9] = yt_ads_df[9].replace("", "0").astype(str).apply(str_to_int)
        yt_ads_df[20] = yt_ads_df[20].replace("", "0").astype(str).apply(str_to_int)
        yt_ads_df[26] = yt_ads_df[26].replace("", "0").astype(str).apply(str_to_int)
        yt_ads_df[29] = yt_ads_df[29].replace("", "0").astype(str).apply(str_to_int)
        yt_ads_df[30] = yt_ads_df[30].replace("", "0").astype(str).apply(extract_int)
        yt_ads_offers = yt_ads_df.groupby(13).apply(lambda x: x.values.tolist())
        yt_ads_data = {}
        for yt_ads_offer in yt_ads_offers:
            offer_name = yt_ads_offer[0][7]
            if offer_name != "":
                total_sales = sum([sales[0] for sales in yt_ads_offer if sales[0] > 0])
                total_revenue = sum(
                    [sales[3] for sales in yt_ads_offer if sales[3] > 0]
                )
                total_impressions = sum(
                    [sales[4] for sales in yt_ads_offer if sales[4] > 0]
                )
                total_clicks = sum([sales[5] for sales in yt_ads_offer if sales[5] > 0])
                total_spend = sum([sales[6] for sales in yt_ads_offer if sales[6] > 0])
                yt_ads_data[offer_name] = {
                    "total_sales": total_sales,
                    "total_revenue": total_revenue,
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_spend": total_spend,
                }
        return yt_ads_data
    except Exception as e:
        return ReportResponse(
            report_title="Get YT Ads Data - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )


# VAI CONSULTAR A TABELA DE ADS E ADS SALES E CONSOLIDAR O RESULTADO
async def get_meta_ads_info():
    pass


async def all_traffic_report(ad_plataform: str):
    # yt_ads_info = await get_yt_ads_info(ad_plataform=ad_plataform)
    player_stats = await get_vturb_info(ad_plataform=ad_plataform)
    return player_stats
