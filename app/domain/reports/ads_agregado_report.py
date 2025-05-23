import os
from datetime import datetime
import pandas as pd

from app.models.report_model import ReportResponse
from app.static_data.active_offers_info import ACTIVE_OFFERS_INFO
from app.core.cleaners import extract_ad_name, extract_offer_name
from app.core.numbers_manipulators import currency_to_int, str_to_int, int_to_currency
from app.external_services.google_sheets import open_spreadsheet, search_worksheet_index
from config import (
    TIMEZONE,
    DB_SPREADSHEET,
    DB_SPREADSHEET_FOLDER_ID,
    REPORT_TYPE_DATA_WORKSHEETS,
    REPORT_TYPE_FRONT_SALES_WORKSHEETS,
    SPREADSHEET_CONTROLE_ADS_ID,
    REPORT_WORKSHEETS,
)


def all_ads_agregado_report(report_type: str):
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
        # return {"data": ads_group}

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
                ads_total_worksheet_index = search_worksheet_index(
                    active_offer_name,
                    SPREADSHEET_CONTROLE_ADS_ID,
                    REPORT_WORKSHEETS["ads_agregado"],
                )
                ads_total_worksheet = trafic_spreadsheet.get_worksheet(
                    ads_total_worksheet_index
                )
                ads_total_worksheet_data = ads_total_worksheet.get_all_values()
                print(
                    f"Oferta {active_offer_name} no índice: {ads_total_worksheet_index}"
                )
                ads_total_df = pd.DataFrame(ads_total_worksheet_data)
                ads_total_df[2] = (
                    ads_total_df[2].astype(str).apply(currency_to_int)
                )  # INVESTIDO
                ads_total_df[3] = (
                    ads_total_df[3].astype(str).apply(currency_to_int)
                )  # FATURAMENTO
                ads_total_df[6] = (
                    ads_total_df[6].astype(str).apply(str_to_int)
                )  # vendas
                ads_total_list = ads_total_df.values.tolist()
                # return {"ads": ads_group}
                row = 0
                for ad in ads_total_list:
                    row += 1
                    ad_name = ad[0]

                    if (
                        ad_name == ""
                        or ad[1] == "😞 Saturou"
                        or ad[1] == ""
                        or ad_name not in ads_group
                    ):
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

                        total_spend = (
                            ads_total_current_spend + new_spend
                            if isinstance(ads_total_current_spend, (int, float))
                            else ads_total_current_spend
                        )
                        total_revenue = (
                            ads_total_current_revenue + new_revenue
                            if isinstance(ads_total_current_revenue, (int, float))
                            else ads_total_current_revenue
                        )
                        total_sales = (
                            ads_total_current_sales + new_sales
                            if isinstance(ads_total_current_sales, (int, float))
                            else ads_total_current_sales
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
                        formatted_total_roas = round(total_roas, 4)
                        formatted_total_cpa = int_to_currency(total_cpa)

                        ad[2] = total_spend
                        ad[3] = total_revenue
                        ad[4] = formatted_total_roas
                        ad[5] = total_cpa
                        ad[6] = total_sales
                        ad[7] = local_time if local_time else ""

                        folder = "email-reports"
                        os.makedirs(folder, exist_ok=True)
                        filename = os.path.join(
                            folder, f"{active_offer_name}_TOTAL.txt"
                        )
                        with open(filename, "a", encoding="utf-8") as file:
                            file.write(f"Anúncio: {ad_name} - Na linha: {row}\n")
                            file.write(
                                f"Valor Gasto Utmify: {new_spend} - Valor Gasto Ads: {ads_total_current_spend} - Total: {total_spend}\n"
                            )
                            file.write(
                                f"Valor Faturado Utmify: {new_revenue} - Valor Faturado Ads: {ads_total_current_revenue} - Total: {total_revenue}\n"
                            )
                            file.write(
                                f"Vendas UTMify: {new_sales} - Vendas Ads: {ads_total_current_sales} - Total: {total_sales}\n"
                            )
                            file.write(
                                f"CPA Total: {formatted_total_cpa} - ROAS Total: {formatted_total_roas}\n"
                            )
                            file.write(f"Atualizado em: {local_time}\n")
                            file.write("-" * 40 + "\n")

                values_to_write_df = pd.DataFrame(ads_total_list)
                values_to_write_df[2] = values_to_write_df[2].apply(
                    int_to_currency
                )  # GASTO
                values_to_write_df[3] = values_to_write_df[3].apply(
                    int_to_currency
                )  # FATURAMENTO
                values_to_write_df[5] = values_to_write_df[5].apply(
                    int_to_currency
                )  # CPA
                values_to_write = values_to_write_df.values.tolist()
                ads_total_worksheet.clear()
                next_row = 1
                ads_total_worksheet.update(
                    f"A{next_row}:I{next_row + len(values_to_write) - 1}",
                    values_to_write,
                )

        return ReportResponse(
            report_title="Write Ads Total Report - Success",
            generated_at=datetime.now(),
            message=f"Ads Total was written successfully!",
            status=200,
        )

    except Exception as e:
        return ReportResponse(
            report_title="Write Ads Total of all offers - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )


def ads_agregado_report(active_offer: str, report_type: str):
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
        # return {"data": ads_group}

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
            ads_total_worksheet_index = search_worksheet_index(
                active_offer_name,
                SPREADSHEET_CONTROLE_ADS_ID,
                REPORT_WORKSHEETS["ads_agregado"],
            )
            ads_total_worksheet = trafic_spreadsheet.get_worksheet(
                ads_total_worksheet_index
            )
            ads_total_worksheet_data = ads_total_worksheet.get_all_values()
            print(f"Oferta {active_offer_name} no índice: {ads_total_worksheet_index}")
            ads_total_df = pd.DataFrame(ads_total_worksheet_data)
            ads_total_df[2] = (
                ads_total_df[2].astype(str).apply(currency_to_int)
            )  # INVESTIDO
            ads_total_df[3] = (
                ads_total_df[3].astype(str).apply(currency_to_int)
            )  # FATURAMENTO
            ads_total_df[6] = ads_total_df[6].astype(str).apply(str_to_int)  # vendas
            ads_total_list = ads_total_df.values.tolist()
            # return {"ads": ads_group}
            row = 0
            for ad in ads_total_list:
                row += 1
                ad_name = ad[0]

                if (
                    ad_name == ""
                    or ad[1] == "😞 Saturou"
                    or ad[1] == ""
                    or ad_name not in ads_group
                ):
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

                    total_spend = (
                        ads_total_current_spend + new_spend
                        if isinstance(ads_total_current_spend, (int, float))
                        else ads_total_current_spend
                    )
                    total_revenue = (
                        ads_total_current_revenue + new_revenue
                        if isinstance(ads_total_current_revenue, (int, float))
                        else ads_total_current_revenue
                    )
                    total_sales = (
                        ads_total_current_sales + new_sales
                        if isinstance(ads_total_current_sales, (int, float))
                        else ads_total_current_sales
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
                    formatted_total_roas = round(total_roas, 4)
                    formatted_total_cpa = int_to_currency(total_cpa)

                    ad[2] = total_spend
                    ad[3] = total_revenue
                    ad[4] = formatted_total_roas
                    ad[5] = total_cpa
                    ad[6] = total_sales
                    ad[7] = local_time if local_time else ""

                    folder = "email-reports"
                    os.makedirs(folder, exist_ok=True)
                    filename = os.path.join(folder, f"{active_offer_name}_TOTAL.txt")
                    with open(filename, "a", encoding="utf-8") as file:
                        file.write(f"Anúncio: {ad_name} - Na linha: {row}\n")
                        file.write(
                            f"Valor Gasto Utmify: {new_spend} - Valor Gasto Ads: {ads_total_current_spend} - Total: {total_spend}\n"
                        )
                        file.write(
                            f"Valor Faturado Utmify: {new_revenue} - Valor Faturado Ads: {ads_total_current_revenue} - Total: {total_revenue}\n"
                        )
                        file.write(
                            f"Vendas UTMify: {new_sales} - Vendas Ads: {ads_total_current_sales} - Total: {total_sales}\n"
                        )
                        file.write(
                            f"CPA Total: {formatted_total_cpa} - ROAS Total: {formatted_total_roas}\n"
                        )
                        file.write(f"Atualizado em: {local_time}\n")
                        file.write("-" * 40 + "\n")

            values_to_write_df = pd.DataFrame(ads_total_list)
            values_to_write_df[2] = values_to_write_df[2].apply(
                int_to_currency
            )  # GASTO
            values_to_write_df[3] = values_to_write_df[3].apply(
                int_to_currency
            )  # FATURAMENTO
            values_to_write_df[5] = values_to_write_df[5].apply(int_to_currency)  # CPA
            values_to_write = values_to_write_df.values.tolist()
            ads_total_worksheet.clear()
            next_row = 1
            ads_total_worksheet.update(
                f"A{next_row}:I{next_row + len(values_to_write) - 1}",
                values_to_write,
            )

        return ReportResponse(
            report_title="Write Ads Total Report - Success",
            generated_at=datetime.now(),
            message=f"Ads Total was written successfully!",
            status=200,
        )

    except Exception as e:
        return ReportResponse(
            report_title="Write Ads Total of all offers - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )
