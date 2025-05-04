import os
from datetime import datetime
import pandas as pd

from app.models.report_model import ReportResponse
from app.external_services.google_sheets import open_spreadsheet, search_worksheet_index
from app.core.numbers_manipulators import str_to_int, currency_to_int, int_to_currency
from app.core.cleaners import extract_ad_name, extract_offer_name
from app.static_data import ACTIVE_OFFERS_INFO

from config import (
    TIMEZONE,
    DB_SPREADSHEET,
    DB_SPREADSHEET_FOLDER_ID,
    SPREADSHEET_CONTROLE_ADS_ID,
    REPORT_TYPE_DATA_WORKSHEETS,
    REPORT_TYPE_FRONT_SALES_WORKSHEETS,
    REPORT_WORKSHEETS,
)


def all_ads_levas_report(report_type: str):
    raw_local_time = datetime.now(TIMEZONE)
    local_time = raw_local_time.strftime("%d/%m/%Y às %Hh%Mmin%Ss")
    try:
        ads_spreadsheet = open_spreadsheet(DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID)
        ads_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_DATA_WORKSHEETS[report_type],
        )
        ads_worksheet = ads_spreadsheet.get_worksheet(ads_worksheet_index)
        ads = ads_worksheet.get_all_values()
        ads_df = pd.DataFrame(ads)
        ads_df = ads_df[ads_df.columns[[10, 14, 19, 25, 27, 28, 46]]]
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
        ads_group = ads_df.groupby(62).apply(lambda x: x.values.tolist())
        offer_group = ads_df.groupby(63).apply(lambda x: x.values.tolist())

        sales_spreadsheet = open_spreadsheet(DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID)
        sales_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_FRONT_SALES_WORKSHEETS[report_type],
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
        sales_ads_group = all_sales_df.groupby(62).apply(lambda x: x.values.tolist())

        for item in ACTIVE_OFFERS_INFO:
            active_offer_name = item["offer_name"]
            if active_offer_name in offer_group:
                print(f"{active_offer_name} teve ocorrencia")
                try:
                    trafic_spreadsheet = open_spreadsheet(
                        active_offer_name, SPREADSHEET_CONTROLE_ADS_ID
                    )
                except Exception as e:
                    print(f"Erro ao abrir a planilha {active_offer_name}: {e}")
                    continue  # Pula para a próxima oferta
                ads_levas_worksheet_index = search_worksheet_index(
                    active_offer_name,
                    SPREADSHEET_CONTROLE_ADS_ID,
                    REPORT_WORKSHEETS["ads_levas"],
                )
                ads_levas_worksheet = trafic_spreadsheet.get_worksheet(
                    ads_levas_worksheet_index
                )
                ads_levas_worksheet_data = ads_levas_worksheet.get_all_values()
                print(
                    f"Oferta {active_offer_name} no índice: {ads_levas_worksheet_index}"
                )
                ads_levas_df = pd.DataFrame(ads_levas_worksheet_data)
                ads_levas_df[7] = (
                    ads_levas_df[7].astype(str).apply(currency_to_int)
                )  # INVESTIDO
                ads_levas_df[8] = (
                    ads_levas_df[8].astype(str).apply(currency_to_int)
                )  # FATURAMENTO
                ads_levas_df[9] = (
                    ads_levas_df[9].astype(str).apply(str_to_int)
                )  # VENDAS
                ads_levas_df[14] = (
                    ads_levas_df[14].astype(str).apply(str_to_int)
                )  # CLICKS
                ads_levas_df[15] = (
                    ads_levas_df[15].astype(str).apply(str_to_int)
                )  # IMPRESSOES
                ads_levas_df[16] = (
                    ads_levas_df[16].astype(str).apply(str_to_int)
                )  # VIDEOS VIEWS
                ads_levas_list = ads_levas_df.values.tolist()

                row = 0
                for ad in ads_levas_list:
                    row += 1
                    if (ad[6] == "⚙️ Testando" or ad[6] == "⏱️ Em validação") and ad[
                        1
                    ] in ads_group:
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

                        new_ctr = (
                            new_link_clicks / new_impressions
                            if new_impressions > 0
                            else 0
                        )
                        new_hook_rate = (
                            new_video_views / new_impressions
                            if new_impressions > 0
                            else 0
                        )
                        new_ctr = round(new_ctr, 4)
                        new_hook_rate = round(new_hook_rate, 4)

                        ads_levas_current_spend = ad[7]
                        ads_levas_current_revenue = ad[8]
                        ads_levas_current_sales = ad[9]
                        ads_levas_current_clicks = ad[14]
                        ads_levas_current_impressions = ad[15]
                        ads_levas_current_video_views = ad[16]

                        total_spend = (
                            ads_levas_current_spend + new_spend
                            if isinstance(ads_levas_current_spend, (int, float))
                            else ads_levas_current_spend
                        )
                        total_revenue = (
                            ads_levas_current_revenue + new_revenue
                            if isinstance(ads_levas_current_revenue, (int, float))
                            else ads_levas_current_revenue
                        )
                        total_sales = (
                            ads_levas_current_sales + new_sales
                            if isinstance(ads_levas_current_sales, (int, float))
                            else ads_levas_current_sales
                        )
                        total_cpa = (
                            int(total_spend / total_sales)
                            if isinstance(total_spend, (int, float))
                            and isinstance(total_sales, (int, float))
                            and total_sales > 0
                            else 0
                        )
                        total_roas = (
                            total_revenue / total_spend
                            if isinstance(total_revenue, int)
                            and isinstance(total_spend, int)
                            and total_spend > 0
                            else 0
                        )
                        total_clicks = (
                            ads_levas_current_clicks + new_link_clicks
                            if isinstance(ads_levas_current_clicks, (int, float))
                            else ads_levas_current_clicks
                        )
                        total_impressions = (
                            ads_levas_current_impressions + new_impressions
                            if isinstance(ads_levas_current_impressions, (int, float))
                            else ads_levas_current_impressions
                        )
                        total_video_views = (
                            ads_levas_current_video_views + new_video_views
                            if isinstance(ads_levas_current_video_views, (int, float))
                            else ads_levas_current_video_views
                        )
                        total_hook = (
                            total_video_views / total_impressions
                            if isinstance(total_video_views, (int, float))
                            and isinstance(total_impressions, (int, float))
                            and total_impressions > 0
                            else total_video_views
                        )
                        total_ctr = (
                            total_clicks / total_impressions
                            if isinstance(total_clicks, (int, float))
                            and isinstance(total_impressions, (int, float))
                            and total_impressions > 0
                            else total_clicks
                        )

                        formated_total_spend = int_to_currency(total_spend)
                        formated_total_revenue = int_to_currency(total_revenue)
                        formated_total_cpa = int_to_currency(total_cpa)
                        formated_total_roas = round(total_roas, 4)

                        ad[7] = total_spend
                        ad[8] = total_revenue
                        ad[9] = total_sales
                        ad[10] = total_cpa
                        ad[11] = formated_total_roas
                        ad[12] = round(total_hook, 4)
                        ad[13] = round(total_ctr, 4)
                        ad[14] = total_clicks
                        ad[15] = total_impressions
                        ad[16] = total_video_views
                        ad[17] = local_time if local_time else ""

                        folder = "email-reports"
                        os.makedirs(folder, exist_ok=True)
                        filename = os.path.join(
                            folder, f"{active_offer_name}_LEVAS.txt"
                        )
                        with open(filename, "a", encoding="utf-8") as file:
                            file.write(f"Anúncio: {ad_name} - Na linha: {row}\n")
                            file.write(
                                f"Valor Gasto Utmify: {new_spend} - Valor Gasto Ads: {ads_levas_current_spend} - Total: {formated_total_spend}\n"
                            )
                            file.write(
                                f"Valor Faturado Utmify: {new_revenue} - Valor Faturado Ads: {ads_levas_current_revenue} - Total: {formated_total_revenue}\n"
                            )
                            file.write(
                                f"Vendas UTMify: {new_sales} - Vendas Ads: {ads_levas_current_sales} - Total: {total_sales}\n"
                            )
                            file.write(
                                f"Cliques UTMify: {new_link_clicks} - Cliques Ads: {ads_levas_current_clicks} - Total: {total_clicks}\n"
                            )
                            file.write(
                                f"Impressões UTMify: {new_impressions} - Impressões Ads: {ads_levas_current_impressions} - Total: {total_impressions}\n"
                            )
                            file.write(
                                f"Videos Views UTMify: {new_video_views} - Videos Views Ads: {ads_levas_current_video_views} - Total: {total_video_views}\n"
                            )
                            file.write(
                                f"HOOK UTMify: {new_hook_rate} - Total: {round(total_hook, 4)}\n"
                            )
                            file.write(
                                f"CTR UTMify: {new_ctr} - Total: {round(total_ctr, 4)}\n"
                            )
                            file.write(
                                f"CPA Total: {formated_total_cpa} - ROAS Total: {formated_total_roas}\n"
                            )
                            file.write(f"Atualizado em: {local_time}\n")
                            file.write("-" * 40 + "\n")

                values_to_write_df = pd.DataFrame(ads_levas_list)
                values_to_write_df[7] = values_to_write_df[7].apply(
                    int_to_currency
                )  # INVESTIDO
                values_to_write_df[8] = values_to_write_df[8].apply(
                    int_to_currency
                )  # FATURAMENTO
                values_to_write_df[10] = values_to_write_df[10].apply(
                    int_to_currency
                )  # CPA
                values_to_write = values_to_write_df.values.tolist()
                # return {"data": offer_group}
                ads_levas_worksheet.clear()
                next_row = 1
                ads_levas_worksheet.update(
                    f"A{next_row}:S{next_row + len(values_to_write) - 1}",
                    values_to_write,
                )
    except Exception as e:
        return ReportResponse(
            report_title="Write Ads Levas of all offers - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )


def ads_levas_report(active_offer: str, report_type: str):
    raw_local_time = datetime.now(TIMEZONE)
    local_time = raw_local_time.strftime("%d/%m/%Y às %Hh%Mmin%Ss")
    try:
        ads_spreadsheet = open_spreadsheet(DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID)
        ads_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_DATA_WORKSHEETS[report_type],
        )
        ads_worksheet = ads_spreadsheet.get_worksheet(ads_worksheet_index)
        ads = ads_worksheet.get_all_values()
        ads_df = pd.DataFrame(ads)
        ads_df = ads_df[ads_df.columns[[10, 14, 19, 25, 27, 28, 46]]]
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
        ads_group = ads_df.groupby(62).apply(lambda x: x.values.tolist())
        offer_group = ads_df.groupby(63).apply(lambda x: x.values.tolist())

        sales_spreadsheet = open_spreadsheet(DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID)
        sales_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_FRONT_SALES_WORKSHEETS[report_type],
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
        sales_ads_group = all_sales_df.groupby(62).apply(lambda x: x.values.tolist())

        active_offer_name = active_offer
        if active_offer_name in offer_group:
            print(f"{active_offer_name} teve ocorrencia")
            try:
                trafic_spreadsheet = open_spreadsheet(
                    active_offer_name, SPREADSHEET_CONTROLE_ADS_ID
                )
            except Exception as e:
                print(f"Erro ao abrir a planilha {active_offer_name}: {e}")
            ads_levas_worksheet_index = search_worksheet_index(
                active_offer_name,
                SPREADSHEET_CONTROLE_ADS_ID,
                REPORT_WORKSHEETS["ads_levas"],
            )
            ads_levas_worksheet = trafic_spreadsheet.get_worksheet(
                ads_levas_worksheet_index
            )
            ads_levas_worksheet_data = ads_levas_worksheet.get_all_values()
            print(f"Oferta {active_offer_name} no índice: {ads_levas_worksheet_index}")
            ads_levas_df = pd.DataFrame(ads_levas_worksheet_data)
            ads_levas_df[7] = (
                ads_levas_df[7].astype(str).apply(currency_to_int)
            )  # INVESTIDO
            ads_levas_df[8] = (
                ads_levas_df[8].astype(str).apply(currency_to_int)
            )  # FATURAMENTO
            ads_levas_df[9] = ads_levas_df[9].astype(str).apply(str_to_int)  # VENDAS
            ads_levas_df[14] = ads_levas_df[14].astype(str).apply(str_to_int)  # CLICKS
            ads_levas_df[15] = (
                ads_levas_df[15].astype(str).apply(str_to_int)
            )  # IMPRESSOES
            ads_levas_df[16] = (
                ads_levas_df[16].astype(str).apply(str_to_int)
            )  # VIDEOS VIEWS
            ads_levas_list = ads_levas_df.values.tolist()

            row = 0
            for ad in ads_levas_list:
                row += 1
                if (ad[6] == "⚙️ Testando" or ad[6] == "⏱️ Em validação") and ad[
                    1
                ] in ads_group:
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

                    new_ctr = (
                        new_link_clicks / new_impressions if new_impressions > 0 else 0
                    )
                    new_hook_rate = (
                        new_video_views / new_impressions if new_impressions > 0 else 0
                    )
                    new_ctr = round(new_ctr, 4)
                    new_hook_rate = round(new_hook_rate, 4)

                    ads_levas_current_spend = ad[7]
                    ads_levas_current_revenue = ad[8]
                    ads_levas_current_sales = ad[9]
                    ads_levas_current_clicks = ad[14]
                    ads_levas_current_impressions = ad[15]
                    ads_levas_current_video_views = ad[16]

                    total_spend = (
                        ads_levas_current_spend + new_spend
                        if isinstance(ads_levas_current_spend, (int, float))
                        else ads_levas_current_spend
                    )
                    total_revenue = (
                        ads_levas_current_revenue + new_revenue
                        if isinstance(ads_levas_current_revenue, (int, float))
                        else ads_levas_current_revenue
                    )
                    total_sales = (
                        ads_levas_current_sales + new_sales
                        if isinstance(ads_levas_current_sales, (int, float))
                        else ads_levas_current_sales
                    )
                    total_cpa = (
                        int(total_spend / total_sales)
                        if isinstance(total_spend, (int, float))
                        and isinstance(total_sales, (int, float))
                        and total_sales > 0
                        else 0
                    )
                    total_roas = (
                        total_revenue / total_spend
                        if isinstance(total_revenue, int)
                        and isinstance(total_spend, int)
                        and total_spend > 0
                        else 0
                    )
                    total_clicks = (
                        ads_levas_current_clicks + new_link_clicks
                        if isinstance(ads_levas_current_clicks, (int, float))
                        else ads_levas_current_clicks
                    )
                    total_impressions = (
                        ads_levas_current_impressions + new_impressions
                        if isinstance(ads_levas_current_impressions, (int, float))
                        else ads_levas_current_impressions
                    )
                    total_video_views = (
                        ads_levas_current_video_views + new_video_views
                        if isinstance(ads_levas_current_video_views, (int, float))
                        else ads_levas_current_video_views
                    )
                    total_hook = (
                        total_video_views / total_impressions
                        if isinstance(total_video_views, (int, float))
                        and isinstance(total_impressions, (int, float))
                        and total_impressions > 0
                        else total_video_views
                    )
                    total_ctr = (
                        total_clicks / total_impressions
                        if isinstance(total_clicks, (int, float))
                        and isinstance(total_impressions, (int, float))
                        and total_impressions > 0
                        else total_clicks
                    )

                    formated_total_spend = int_to_currency(total_spend)
                    formated_total_revenue = int_to_currency(total_revenue)
                    formated_total_cpa = int_to_currency(total_cpa)
                    formated_total_roas = round(total_roas, 4)

                    ad[7] = total_spend
                    ad[8] = total_revenue
                    ad[9] = total_sales
                    ad[10] = total_cpa
                    ad[11] = formated_total_roas
                    ad[12] = round(total_hook, 4)
                    ad[13] = round(total_ctr, 4)
                    ad[14] = total_clicks
                    ad[15] = total_impressions
                    ad[16] = total_video_views
                    ad[17] = local_time if local_time else ""

                    folder = "email-reports"
                    os.makedirs(folder, exist_ok=True)
                    filename = os.path.join(folder, f"{active_offer_name}_LEVAS.txt")
                    with open(filename, "a", encoding="utf-8") as file:
                        file.write(f"Anúncio: {ad_name} - Na linha: {row}\n")
                        file.write(
                            f"Valor Gasto Utmify: {new_spend} - Valor Gasto Ads: {ads_levas_current_spend} - Total: {formated_total_spend}\n"
                        )
                        file.write(
                            f"Valor Faturado Utmify: {new_revenue} - Valor Faturado Ads: {ads_levas_current_revenue} - Total: {formated_total_revenue}\n"
                        )
                        file.write(
                            f"Vendas UTMify: {new_sales} - Vendas Ads: {ads_levas_current_sales} - Total: {total_sales}\n"
                        )
                        file.write(
                            f"Cliques UTMify: {new_link_clicks} - Cliques Ads: {ads_levas_current_clicks} - Total: {total_clicks}\n"
                        )
                        file.write(
                            f"Impressões UTMify: {new_impressions} - Impressões Ads: {ads_levas_current_impressions} - Total: {total_impressions}\n"
                        )
                        file.write(
                            f"Videos Views UTMify: {new_video_views} - Videos Views Ads: {ads_levas_current_video_views} - Total: {total_video_views}\n"
                        )
                        file.write(
                            f"HOOK UTMify: {new_hook_rate} - Total: {round(total_hook, 4)}\n"
                        )
                        file.write(
                            f"CTR UTMify: {new_ctr} - Total: {round(total_ctr, 4)}\n"
                        )
                        file.write(
                            f"CPA Total: {formated_total_cpa} - ROAS Total: {formated_total_roas}\n"
                        )
                        file.write(f"Atualizado em: {local_time}\n")
                        file.write("-" * 40 + "\n")

            values_to_write_df = pd.DataFrame(ads_levas_list)
            values_to_write_df[7] = values_to_write_df[7].apply(
                int_to_currency
            )  # INVESTIDO
            values_to_write_df[8] = values_to_write_df[8].apply(
                int_to_currency
            )  # FATURAMENTO
            values_to_write_df[10] = values_to_write_df[10].apply(
                int_to_currency
            )  # CPA
            values_to_write = values_to_write_df.values.tolist()
            ads_levas_worksheet.clear()
            next_row = 1
            ads_levas_worksheet.update(
                f"A{next_row}:ZZ{next_row + len(values_to_write) - 1}",
                values_to_write,
            )

    except Exception as e:
        return ReportResponse(
            report_title="Write Ads Levas of all offers - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )
