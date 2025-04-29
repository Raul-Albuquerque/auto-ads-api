import os
from datetime import datetime, timedelta
import pandas as pd

from app.models.report_model import ReportResponse
from app.external_services.google_sheets import open_spreadsheet, search_worksheet_index
from app.core.cleaners import (
    extract_offer_name,
    extract_player_offer_name,
    extract_player_plataform,
    extract_ad_block,
    extract_ad_name,
)
from app.core.helpers import process_data, formatted_date
from app.core.compute_metrics import compute_metrics
from app.core.numbers_manipulators import str_to_int, extract_int, int_to_currency
from app.static_data.active_offers_info import ACTIVE_OFFERS_INFO
from config import (
    DB_SPREADSHEET,
    DB_SPREADSHEET_FOLDER_ID,
    REPORT_TYPE_DATA_WORKSHEETS,
    REPORT_TYPE_FRONT_SALES_WORKSHEETS,
    SPREADSHEET_TRAFFIC_CONTROL_ID,
    REPORT_WORKSHEETS,
)


# VAI CONSULTAR A TABELA DO VTURB E RETORNAR OS DADOS
async def get_vturb_info():
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
        player_stats_df = pd.DataFrame(player_stats)
        player_stats_df = player_stats_df.drop(player_stats_df.columns[[5]], axis=1)
        player_stats_df[2] = (
            player_stats_df[2].replace("", "0").astype(str).apply(str_to_int)
        )
        player_stats_df[3] = (
            player_stats_df[3].replace("", "0").astype(str).apply(str_to_int)
        )
        player_stats_df[4] = (
            player_stats_df[4].replace("", "0").astype(str).apply(str_to_int)
        )
        player_stats_df[6] = (
            player_stats_df[1]
            .replace("", "0")
            .astype(str)
            .apply(extract_player_offer_name)
        )
        player_stats_df[7] = (
            player_stats_df[1]
            .replace("", "0")
            .astype(str)
            .apply(extract_player_plataform)
        )
        raw_player_stats_by_plataform = player_stats_df.groupby(6).apply(
            lambda x: x.values.tolist()
        )
        player_stats_by_plataform = process_data(raw_player_stats_by_plataform)
        return player_stats_by_plataform

    except Exception as e:
        return ReportResponse(
            report_title="Get Vturb Info - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )


async def get_yt_ads_info():
    try:
        yt_ads_sales_spreadsheet = open_spreadsheet(
            DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID
        )
        yt_ads_sales_spreadsheet_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_FRONT_SALES_WORKSHEETS["yt_ads"],
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
            REPORT_TYPE_DATA_WORKSHEETS["yt_ads"],
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
    try:
        ads_spreadsheet = open_spreadsheet(DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID)
        ads_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_DATA_WORKSHEETS["controle_ads"],
        )
        ads_worksheet = ads_spreadsheet.get_worksheet(ads_worksheet_index)
        ads = ads_worksheet.get_all_values()
        ads_df = pd.DataFrame(ads)
        ads_df = ads_df[ads_df.columns[[10, 14, 19, 25, 27, 28, 29, 46]]]
        ads_df[10] = ads_df[10].replace("", "0").astype(str).apply(str_to_int)  # SALES
        ads_df[19] = (
            ads_df[19].replace("", "0").astype(str).apply(str_to_int)
        )  # REVENUE
        ads_df[28] = ads_df[28].replace("", "0").astype(str).apply(str_to_int)  # SPEND
        ads_df[25] = (
            ads_df[25].replace("", "0").astype(str).apply(str_to_int)
        )  # IMPRESSIONS
        ads_df[27] = (
            ads_df[27].replace("", "0").astype(str).apply(str_to_int)
        )  # INLINELINKCLICKS
        ads_df[46] = (
            ads_df[46].replace("", "0").astype(str).apply(str_to_int)
        )  # VIDEOVIEWS3S
        ads_df[62] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_ad_name)
        )  # AD NAME
        ads_df[63] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_offer_name)
        )  # OFFER
        ads_df[64] = (
            ads_df[29].replace("", "0").astype(str).apply(str_to_int)
        )  # INITIATE CHECKOUT
        ads_df = ads_df.drop(ads_df.columns[6], axis=1)
        offers_group = ads_df.groupby(63).apply(lambda x: x.values.tolist())

        sales_spreadsheet = open_spreadsheet(DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID)
        sales_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_FRONT_SALES_WORKSHEETS["controle_ads"],
        )
        sales_worksheet = sales_spreadsheet.get_worksheet(sales_worksheet_index)
        all_sales = sales_worksheet.get_all_values()
        all_sales_df = pd.DataFrame(all_sales)
        all_sales_df[10] = (
            all_sales_df[10].replace("", "0").astype(str).apply(str_to_int)
        )  # SALES
        all_sales_df[62] = (
            all_sales_df[14].replace("", "0").astype(str).apply(extract_ad_name)
        )  # AD NAME
        all_sales_df[63] = (
            all_sales_df[14].replace("", "0").astype(str).apply(extract_offer_name)
        )  # OFFER
        all_sales_df = all_sales_df[all_sales_df.columns[[10, 62, 63]]]
        sales_ads_group = all_sales_df.groupby(63).apply(lambda x: x.values.tolist())
        meta_ads_data = {}
        for offer in offers_group:
            offer_name = offer[0][8]
            if offer_name != "":
                total_revenue = sum([item[2] for item in offer])
                total_impressions = sum([item[3] for item in offer])
                total_clicks = sum([item[4] for item in offer])
                total_spend = sum([item[5] for item in offer])
                total_sales = sum([item[0] for item in sales_ads_group[offer_name]])
                total_initiante_checkout = sum([item[9] for item in offer])
                meta_ads_data[offer_name] = {
                    "total_sales": total_sales,
                    "total_revenue": total_revenue,
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_spend": total_spend,
                    "total_initiate_checkout": total_initiante_checkout,
                }
        return meta_ads_data

    except Exception as e:
        return ReportResponse(
            report_title="Get Meta Ads Data - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )


async def traffic_report(active_offer: str, report_type: str, day: str):
    yt_ads_info = await get_yt_ads_info()
    player_stats = await get_vturb_info()
    spreadsheet_name = f"[{active_offer}] - Controle de Tráfego"
    meta_ads_info = await get_meta_ads_info()
    try:
        traffic_control_spreadsheet = open_spreadsheet(
            spreadsheet_name, SPREADSHEET_TRAFFIC_CONTROL_ID
        )
        traffic_control_worksheet_index = search_worksheet_index(
            spreadsheet_name,
            SPREADSHEET_TRAFFIC_CONTROL_ID,
            REPORT_WORKSHEETS[report_type],
        )
        traffic_control_worksheet = traffic_control_spreadsheet.get_worksheet(
            traffic_control_worksheet_index
        )
        traffic_control = traffic_control_worksheet.get_all_values()
        facebook_ads = [item for item in traffic_control[20:45]]

        facebook_daily_player_stats = player_stats[active_offer].get("FB", False)
        facebook_daily_uniq_views = (
            facebook_daily_player_stats.get("sum_total_uniq")
            if facebook_daily_player_stats
            else 0
        )
        facebook_daily_over_pitch = (
            facebook_daily_player_stats.get("sum_over_pitch")
            if facebook_daily_player_stats
            else 0
        )
        facebook_daily_under_pitch = (
            facebook_daily_player_stats.get("sum_under_pitch")
            if facebook_daily_player_stats
            else 0
        )
        facebook_daily_spend = meta_ads_info[active_offer].get("total_spend", 0)
        facebook_daily_revenue = meta_ads_info[active_offer].get("total_revenue", 0)
        facebook_daily_sales = meta_ads_info[active_offer].get("total_sales", 0)
        facebook_daily_impressions = meta_ads_info[active_offer].get(
            "total_impressions", 0
        )
        facebook_daily_clicks = meta_ads_info[active_offer].get("total_clicks", 0)
        facebook_daily_initiate_checkout = meta_ads_info[active_offer].get(
            "total_initiate_checkout", 0
        )
        facebook_checkout_rate = (
            round(facebook_daily_sales / facebook_daily_initiate_checkout, 4)
            if facebook_daily_initiate_checkout > 0
            else 0
        )
        derived_metrics = compute_metrics(
            spend=facebook_daily_spend,
            revenue=facebook_daily_revenue,
            sales=facebook_daily_sales,
            uniq_views=facebook_daily_uniq_views,
            clicks=facebook_daily_clicks,
            impressions=facebook_daily_impressions,
            total_over_pitch=facebook_daily_over_pitch,
            total_under_pitch=facebook_daily_under_pitch,
        )
        facebook_ads[0].append("")
        facebook_ads[1].append(int_to_currency(facebook_daily_spend))  # Investimento
        facebook_ads[2].append(int_to_currency(facebook_daily_revenue))  # faturamento
        facebook_ads[3].append(derived_metrics.get("roas"))
        facebook_ads[4].append(derived_metrics.get("gross_profit"))
        facebook_ads[5].append(derived_metrics.get("cpa"))
        facebook_ads[6].append(facebook_daily_uniq_views)
        facebook_ads[7].append(facebook_daily_sales)
        facebook_ads[8].append(derived_metrics.get("pitch_retention"))
        facebook_ads[9].append(derived_metrics.get("vsl_conversion"))
        facebook_ads[10].append(derived_metrics.get("arpu"))
        facebook_ads[11].append("")
        facebook_ads[12].append(derived_metrics.get("connect_rate"))
        facebook_ads[13].append(facebook_daily_clicks)
        facebook_ads[14].append(derived_metrics.get("cpc"))
        facebook_ads[15].append(derived_metrics.get("a_cpc"))
        facebook_ads[16].append(derived_metrics.get("rpc"))
        facebook_ads[17].append(derived_metrics.get("ctr"))
        facebook_ads[18].append(facebook_checkout_rate)
        facebook_ads[19].append(derived_metrics.get("cpm"))
        facebook_ads[20].append(0)
        facebook_ads[21].append(facebook_daily_impressions)
        facebook_ads[22].append(facebook_daily_over_pitch)
        facebook_ads[23].append(facebook_daily_under_pitch)
        facebook_ads[24].append(facebook_daily_initiate_checkout)
        facebook_ads[1][2] = "=SOMA(D22:ZZ22)"  # spend
        facebook_ads[2][2] = "=SOMA(D23:ZZ23)"  # revenue
        facebook_ads[3][2] = "=SE(C22>0;C23/C22;0)"  # ROAS
        facebook_ads[4][2] = "=C23-C22"  # GROSS PROFIT
        facebook_ads[5][2] = "=SE(C28>0;C22/C28;0)"  # CPA
        facebook_ads[6][2] = "=SOMA(D27:ZZ27)"  # VIEWS
        facebook_ads[7][2] = "=SOMA(D28:ZZ28)"  # SALES
        facebook_ads[8][2] = "=C43 / SOMA(C43:C44)"  # PITCH RETENTION
        facebook_ads[9][2] = "=SE(C27>0;C28/C27;0)"  # VSL CONVERSION
        facebook_ads[10][2] = "=SE(C28>0;C23/C28;0)"  # ARPU
        facebook_ads[12][2] = "=SE(C34>0;C27/C34;0)"  # CONNECT RATE
        facebook_ads[13][2] = "=SOMA(D34:ZZ34)"  # CLIQUES
        facebook_ads[14][2] = "=SE(C34>0;C22/C34;0)"  # CPC
        facebook_ads[15][2] = "=SEERRO(C30 * C31/'Configurações'!B2; 0)"  # ACPC
        facebook_ads[16][2] = "=SE(C34>0;C23/C34;0)"  # RPC
        facebook_ads[17][2] = "=SE(C42>0;C34/C42;0)"  # CTR
        facebook_ads[18][2] = "=SE(C45>0;C28/C45;0)"  # CHECKOUT
        facebook_ads[19][2] = "=C22/C42 * 1000"  # CPM
        facebook_ads[20][2] = "0"  # FREQUENCIA
        facebook_ads[21][2] = "=SOMA(D42:ZZ42)"  # IMPRESSOES
        facebook_ads[22][2] = "=SOMA(D43:ZZ43)"  # OVER PITCH
        facebook_ads[23][2] = "=SOMA(D44:ZZ44)"  # UNDER PITCH
        facebook_ads[24][2] = "=SOMA(D45:ZZ45)"  # INITIATE CHECKOUT

        traffic_control[20:45] = facebook_ads

        youtube_ads = [item for item in traffic_control[45:]]
        youtube_daily_player_stats = player_stats[active_offer].get("YT", False)
        youtube_daily_uniq_views = (
            youtube_daily_player_stats.get("sum_total_uniq")
            if youtube_daily_player_stats
            else 0
        )
        youtube_daily_over_pitch = (
            youtube_daily_player_stats.get("sum_over_pitch")
            if youtube_daily_player_stats
            else 0
        )
        youtube_daily_under_pitch = (
            youtube_daily_player_stats.get("sum_under_pitch")
            if youtube_daily_player_stats
            else 0
        )
        youtube_daily_spend = yt_ads_info[active_offer].get("total_spend", 0)
        youtube_daily_revenue = yt_ads_info[active_offer].get("total_revenue", 0)
        youtube_daily_sales = yt_ads_info[active_offer].get("total_sales", 0)
        youtube_daily_impressions = yt_ads_info[active_offer].get(
            "total_impressions", 0
        )
        youtube_daily_clicks = yt_ads_info[active_offer].get("total_clicks", 0)
        derived_metrics = compute_metrics(
            spend=youtube_daily_spend,
            revenue=youtube_daily_revenue,
            sales=youtube_daily_sales,
            uniq_views=youtube_daily_uniq_views,
            clicks=youtube_daily_clicks,
            impressions=youtube_daily_impressions,
            total_over_pitch=youtube_daily_over_pitch,
            total_under_pitch=youtube_daily_under_pitch,
        )

        youtube_ads[0].append("")
        youtube_ads[1].append(int_to_currency(youtube_daily_spend))
        youtube_ads[2].append(int_to_currency(youtube_daily_revenue))
        youtube_ads[3].append(derived_metrics.get("roas"))
        youtube_ads[4].append(derived_metrics.get("gross_profit"))
        youtube_ads[5].append(youtube_daily_uniq_views)
        youtube_ads[6].append(youtube_daily_sales)
        youtube_ads[7].append(derived_metrics.get("vsl_conversion"))
        youtube_ads[8].append(derived_metrics.get("arpu"))
        youtube_ads[9].append("")
        youtube_ads[10].append(derived_metrics.get("connect_rate"))
        youtube_ads[11].append(youtube_daily_clicks)
        youtube_ads[12].append(derived_metrics.get("cpc"))
        youtube_ads[13].append(derived_metrics.get("a_cpc"))
        youtube_ads[14].append(derived_metrics.get("rpc"))
        youtube_ads[15].append(derived_metrics.get("ctr"))
        youtube_ads[16].append("")
        youtube_ads[17].append("")
        youtube_ads[18].append(youtube_daily_impressions)
        youtube_ads[19].append(youtube_daily_over_pitch)
        youtube_ads[20].append(youtube_daily_under_pitch)
        youtube_ads[1][2] = "=SOMA(D47:ZZ47)"  # spend
        youtube_ads[2][2] = "=SOMA(D48:ZZ48)"  # revenue
        youtube_ads[3][2] = "=SE(C47>0;C48/C47;0)"  # ROAS
        youtube_ads[4][2] = "=C48-C47"  # GROSS PROFIT
        youtube_ads[5][2] = "=SOMA(D51:ZZ51)"  # VIEWS
        youtube_ads[6][2] = "=SOMA(D52:ZZ52)"  # SALES
        youtube_ads[7][2] = "=SE(C51>0;C52/C51;0)"  # VSL CONVERSION
        youtube_ads[8][2] = "=SE(C52>0;C48/C52;0)"  # ARPU
        youtube_ads[10][2] = "=SE(C57>0;C51/C57;0)"  # CONNECT RATE
        youtube_ads[11][2] = "=SOMA(D57:ZZ57)"  # CLIQUES
        youtube_ads[12][2] = "=SE(C57>0;C47/C57;0)"  # CPC
        youtube_ads[13][2] = "=SEERRO(C53 * C54/'Configurações'!B2; 0)"  # ACPC
        youtube_ads[14][2] = "=SE(C57>0;C48/C57;0)"  # RPC
        youtube_ads[15][2] = "=SE(C64>0;C57/C64;0)"  # CTR
        youtube_ads[17][2] = ""  # FREQUENCIA
        youtube_ads[18][2] = "=SOMA(D64:ZZ64)"  # IMPRESSOES
        youtube_ads[19][2] = "=SOMA(D65:ZZ65)"  # OVER PITCH
        youtube_ads[20][2] = "=SOMA(D66:ZZ66)"  # UNDER PITCH
        traffic_control[45:] = youtube_ads

        date = formatted_date(day=day)
        traffic_control[1].append(date)
        next_row = 1
        traffic_control_worksheet.update(
            f"A{next_row}:ZZ{next_row + len(traffic_control) - 1}",
            traffic_control,
            value_input_option="USER_ENTERED",
        )
        return ReportResponse(
            report_title="Write traffic control - Success",
            generated_at=datetime.now(),
            message=f"Relatórios de traffic control escrito com sucesso!",
            status=200,
        )
    except Exception as e:
        return ReportResponse(
            report_title="traffic control - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )


async def all_traffic_report(report_type: str, day: str):
    yt_ads_info = await get_yt_ads_info()
    player_stats = await get_vturb_info()
    meta_ads_info = await get_meta_ads_info()

    for active_offer_item in ACTIVE_OFFERS_INFO:
        active_offer = active_offer_item["offer_name"]
        spreadsheet_name = f"[{active_offer}] - Controle de Tráfego"
        if active_offer not in meta_ads_info and active_offer not in yt_ads_info:
            print(f"{active_offer} não teve ocorrências")
            continue
        try:
            traffic_control_spreadsheet = open_spreadsheet(
                spreadsheet_name, SPREADSHEET_TRAFFIC_CONTROL_ID
            )
            traffic_control_worksheet_index = search_worksheet_index(
                spreadsheet_name,
                SPREADSHEET_TRAFFIC_CONTROL_ID,
                REPORT_WORKSHEETS[report_type],
            )
            traffic_control_worksheet = traffic_control_spreadsheet.get_worksheet(
                traffic_control_worksheet_index
            )
            traffic_control = traffic_control_worksheet.get_all_values()
            facebook_ads = [item for item in traffic_control[20:45]]

            facebook_daily_player_stats = player_stats[active_offer].get("FB", False)
            facebook_daily_uniq_views = (
                facebook_daily_player_stats.get("sum_total_uniq")
                if facebook_daily_player_stats
                else 0
            )
            facebook_daily_over_pitch = (
                facebook_daily_player_stats.get("sum_over_pitch")
                if facebook_daily_player_stats
                else 0
            )
            facebook_daily_under_pitch = (
                facebook_daily_player_stats.get("sum_under_pitch")
                if facebook_daily_player_stats
                else 0
            )
            facebook_daily_spend = meta_ads_info[active_offer].get("total_spend", 0)
            facebook_daily_revenue = meta_ads_info[active_offer].get("total_revenue", 0)
            facebook_daily_sales = meta_ads_info[active_offer].get("total_sales", 0)
            facebook_daily_impressions = meta_ads_info[active_offer].get(
                "total_impressions", 0
            )
            facebook_daily_clicks = meta_ads_info[active_offer].get("total_clicks", 0)
            facebook_daily_initiate_checkout = meta_ads_info[active_offer].get(
                "total_initiate_checkout", 0
            )
            facebook_checkout_rate = (
                round(facebook_daily_sales / facebook_daily_initiate_checkout, 4)
                if facebook_daily_initiate_checkout > 0
                else 0
            )
            derived_metrics = compute_metrics(
                spend=facebook_daily_spend,
                revenue=facebook_daily_revenue,
                sales=facebook_daily_sales,
                uniq_views=facebook_daily_uniq_views,
                clicks=facebook_daily_clicks,
                impressions=facebook_daily_impressions,
                total_over_pitch=facebook_daily_over_pitch,
                total_under_pitch=facebook_daily_under_pitch,
            )
            facebook_ads[0].append("")
            facebook_ads[1].append(
                int_to_currency(facebook_daily_spend)
            )  # Investimento
            facebook_ads[2].append(
                int_to_currency(facebook_daily_revenue)
            )  # faturamento
            facebook_ads[3].append(derived_metrics.get("roas"))
            facebook_ads[4].append(derived_metrics.get("gross_profit"))
            facebook_ads[5].append(derived_metrics.get("cpa"))
            facebook_ads[6].append(facebook_daily_uniq_views)
            facebook_ads[7].append(facebook_daily_sales)
            facebook_ads[8].append(derived_metrics.get("pitch_retention"))
            facebook_ads[9].append(derived_metrics.get("vsl_conversion"))
            facebook_ads[10].append(derived_metrics.get("arpu"))
            facebook_ads[11].append("")
            facebook_ads[12].append(derived_metrics.get("connect_rate"))
            facebook_ads[13].append(facebook_daily_clicks)
            facebook_ads[14].append(derived_metrics.get("cpc"))
            facebook_ads[15].append(derived_metrics.get("a_cpc"))
            facebook_ads[16].append(derived_metrics.get("rpc"))
            facebook_ads[17].append(derived_metrics.get("ctr"))
            facebook_ads[18].append(facebook_checkout_rate)
            facebook_ads[19].append(derived_metrics.get("cpm"))
            facebook_ads[20].append(0)
            facebook_ads[21].append(facebook_daily_impressions)
            facebook_ads[22].append(facebook_daily_over_pitch)
            facebook_ads[23].append(facebook_daily_under_pitch)
            facebook_ads[24].append(facebook_daily_initiate_checkout)
            facebook_ads[1][2] = "=SOMA(D22:ZZ22)"  # spend
            facebook_ads[2][2] = "=SOMA(D23:ZZ23)"  # revenue
            facebook_ads[3][2] = "=SE(C22>0;C23/C22;0)"  # ROAS
            facebook_ads[4][2] = "=C23-C22"  # GROSS PROFIT
            facebook_ads[5][2] = "=SE(C28>0;C22/C28;0)"  # CPA
            facebook_ads[6][2] = "=SOMA(D27:ZZ27)"  # VIEWS
            facebook_ads[7][2] = "=SOMA(D28:ZZ28)"  # SALES
            facebook_ads[8][2] = "=C43 / SOMA(C43:C44)"  # PITCH RETENTION
            facebook_ads[9][2] = "=SE(C27>0;C28/C27;0)"  # VSL CONVERSION
            facebook_ads[10][2] = "=SE(C28>0;C23/C28;0)"  # ARPU
            facebook_ads[12][2] = "=SE(C34>0;C27/C34;0)"  # CONNECT RATE
            facebook_ads[13][2] = "=SOMA(D34:ZZ34)"  # CLIQUES
            facebook_ads[14][2] = "=SE(C34>0;C22/C34;0)"  # CPC
            facebook_ads[15][2] = "=SEERRO(C30 * C31/'Configurações'!B2; 0)"  # ACPC
            facebook_ads[16][2] = "=SE(C34>0;C23/C34;0)"  # RPC
            facebook_ads[17][2] = "=SE(C42>0;C34/C42;0)"  # CTR
            facebook_ads[18][2] = "=SE(C45>0;C28/C45;0)"  # CHECKOUT
            facebook_ads[19][2] = "=C22/C42 * 1000"  # CPM
            facebook_ads[20][2] = "0"  # FREQUENCIA
            facebook_ads[21][2] = "=SOMA(D42:ZZ42)"  # IMPRESSOES
            facebook_ads[22][2] = "=SOMA(D43:ZZ43)"  # OVER PITCH
            facebook_ads[23][2] = "=SOMA(D44:ZZ44)"  # UNDER PITCH
            facebook_ads[24][2] = "=SOMA(D45:ZZ45)"  # INITIATE CHECKOUT

            traffic_control[20:45] = facebook_ads

            youtube_ads = [item for item in traffic_control[45:]]
            youtube_daily_player_stats = player_stats[active_offer].get("YT", False)
            youtube_daily_uniq_views = (
                youtube_daily_player_stats.get("sum_total_uniq")
                if youtube_daily_player_stats
                else 0
            )
            youtube_daily_over_pitch = (
                youtube_daily_player_stats.get("sum_over_pitch")
                if youtube_daily_player_stats
                else 0
            )
            youtube_daily_under_pitch = (
                youtube_daily_player_stats.get("sum_under_pitch")
                if youtube_daily_player_stats
                else 0
            )
            youtube_daily_spend = yt_ads_info[active_offer].get("total_spend", 0)
            youtube_daily_revenue = yt_ads_info[active_offer].get("total_revenue", 0)
            youtube_daily_sales = yt_ads_info[active_offer].get("total_sales", 0)
            youtube_daily_impressions = yt_ads_info[active_offer].get(
                "total_impressions", 0
            )
            youtube_daily_clicks = yt_ads_info[active_offer].get("total_clicks", 0)
            derived_metrics = compute_metrics(
                spend=youtube_daily_spend,
                revenue=youtube_daily_revenue,
                sales=youtube_daily_sales,
                uniq_views=youtube_daily_uniq_views,
                clicks=youtube_daily_clicks,
                impressions=youtube_daily_impressions,
                total_over_pitch=youtube_daily_over_pitch,
                total_under_pitch=youtube_daily_under_pitch,
            )

            youtube_ads[0].append("")
            youtube_ads[1].append(int_to_currency(youtube_daily_spend))
            youtube_ads[2].append(int_to_currency(youtube_daily_revenue))
            youtube_ads[3].append(derived_metrics.get("roas"))
            youtube_ads[4].append(derived_metrics.get("gross_profit"))
            youtube_ads[5].append(youtube_daily_uniq_views)
            youtube_ads[6].append(youtube_daily_sales)
            youtube_ads[7].append(derived_metrics.get("vsl_conversion"))
            youtube_ads[8].append(derived_metrics.get("arpu"))
            youtube_ads[9].append("")
            youtube_ads[10].append(derived_metrics.get("connect_rate"))
            youtube_ads[11].append(youtube_daily_clicks)
            youtube_ads[12].append(derived_metrics.get("cpc"))
            youtube_ads[13].append(derived_metrics.get("a_cpc"))
            youtube_ads[14].append(derived_metrics.get("rpc"))
            youtube_ads[15].append(derived_metrics.get("ctr"))
            youtube_ads[16].append("")
            youtube_ads[17].append(0)
            youtube_ads[18].append(youtube_daily_impressions)
            youtube_ads[19].append(youtube_daily_over_pitch)
            youtube_ads[20].append(youtube_daily_under_pitch)
            youtube_ads[1][2] = "=SOMA(D47:ZZ47)"  # spend
            youtube_ads[2][2] = "=SOMA(D48:ZZ48)"  # revenue
            youtube_ads[3][2] = "=SE(C47>0;C48/C47;0)"  # ROAS
            youtube_ads[4][2] = "=C48-C47"  # GROSS PROFIT
            youtube_ads[5][2] = "=SOMA(D51:ZZ51)"  # VIEWS
            youtube_ads[6][2] = "=SOMA(D52:ZZ52)"  # SALES
            youtube_ads[7][2] = "=SE(C51>0;C52/C51;0)"  # VSL CONVERSION
            youtube_ads[8][2] = "=SE(C52>0;C48/C52;0)"  # ARPU
            youtube_ads[10][2] = "=SE(C57>0;C51/C57;0)"  # CONNECT RATE
            youtube_ads[11][2] = "=SOMA(D57:ZZ57)"  # CLIQUES
            youtube_ads[12][2] = "=SE(C57>0;C47/C57;0)"  # CPC
            youtube_ads[13][2] = "=SEERRO(C53 * C54/'Configurações'!B2; 0)"  # ACPC
            youtube_ads[14][2] = "=SE(C57>0;C48/C57;0)"  # RPC
            youtube_ads[15][2] = "=SE(C64>0;C57/C64;0)"  # CTR
            youtube_ads[17][2] = "0"  # FREQUENCIA
            youtube_ads[18][2] = "=SOMA(D64:ZZ64)"  # IMPRESSOES
            youtube_ads[19][2] = "=SOMA(D65:ZZ65)"  # OVER PITCH
            youtube_ads[20][2] = "=SOMA(D66:ZZ66)"  # UNDER PITCH
            traffic_control[45:] = youtube_ads

            date = formatted_date(day=day)
            traffic_control[1].append(date)
            next_row = 1
            traffic_control_worksheet.update(
                f"A{next_row}:ZZ{next_row + len(traffic_control) - 1}",
                traffic_control,
                value_input_option="USER_ENTERED",
            )
        except Exception as e:
            print(e)
            continue

    return ReportResponse(
        report_title="Write traffic control - Success",
        generated_at=datetime.now(),
        message=f"Relatórios de traffic control escrito com sucesso!",
        status=200,
    )
