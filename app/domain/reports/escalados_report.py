import os
from datetime import datetime, timedelta
from time import sleep
import pandas as pd

from app.models.report_model import ReportResponse
from app.static_data.active_offers_info import ACTIVE_OFFERS_INFO
from app.external_services.google_sheets import (
    open_spreadsheet,
    search_worksheet_index,
    duplicate_template_sheet_to_end,
)
from app.core.numbers_manipulators import str_to_int, int_to_currency, currency_to_int
from app.core.cleaners import extract_ad_block
from config import (
    TIMEZONE,
    DB_SPREADSHEET,
    DB_SPREADSHEET_FOLDER_ID,
    REPORT_TYPE_DATA_WORKSHEETS,
    REPORT_TYPE_FRONT_SALES_WORKSHEETS,
    SPREADSHEET_ESCALADOS_ID,
    REPORT_WORKSHEETS,
)


def all_ads_escalados_report(report_type: str, period: str):
    raw_local_time = datetime.now(TIMEZONE)
    raw_yesterday = raw_local_time - timedelta(days=1)
    local_time = raw_local_time.strftime("%d/%m/%Y às %Hh%Mmin%Ss")
    local_date = (
        raw_local_time.strftime("%d/%m/%Y")
        if period == "today"
        else raw_yesterday.strftime("%d/%m/%Y")
    )
    try:
        sales_spreadsheet = open_spreadsheet(DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID)
        sleep(1)
        sales_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_FRONT_SALES_WORKSHEETS[report_type],
        )
        sales_worksheet = sales_spreadsheet.get_worksheet(sales_worksheet_index)
        all_sales = sales_worksheet.get_all_values()
        sleep(1)
        all_sales_df = pd.DataFrame(all_sales)
        all_sales_df[10] = (
            all_sales_df[10].replace("", "0").astype(str).apply(str_to_int)
        )  # SALES
        all_sales_df = all_sales_df[all_sales_df.columns[[3, 10]]]
        sales_ads_list = all_sales_df.groupby(3).apply(lambda x: x.values.tolist())
        campaigns_spreadsheet = open_spreadsheet(
            DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID
        )
        campaigns_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_DATA_WORKSHEETS[report_type],
        )
        campaigns_worksheet = campaigns_spreadsheet.get_worksheet(
            campaigns_worksheet_index
        )
        campaigns = campaigns_worksheet.get_all_values()
        sleep(1)
        for campaign in campaigns[1:]:
            campaign_id = campaign[3]
            campaign[10] = sales_ads_list[campaign_id][0][1]
        ads_df = pd.DataFrame(campaigns)
        ads_df = ads_df[ads_df.columns[[3, 10, 14, 17, 19, 28]]]
        ads_df[17] = (
            ads_df[17].replace("", "0").astype(str).apply(str_to_int)
        )  # DAILY BUDGET
        ads_df[19] = (
            ads_df[19].replace("", "0").astype(str).apply(str_to_int)
        )  # REVENUE
        ads_df[28] = ads_df[28].replace("", "0").astype(str).apply(str_to_int)  # SPEND
        ads_df[63] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_ad_block)
        )  # AD NAME
        ads_group = ads_df.groupby(63).apply(lambda x: x.values.tolist())

        for active_offer_item in ACTIVE_OFFERS_INFO:
            active_offer = active_offer_item["offer_name"]
            try:
                ads_escalados_spreadsheet = open_spreadsheet(
                    active_offer, SPREADSHEET_ESCALADOS_ID
                )
                sleep(1)
                ads_escalados_worksheet_index = search_worksheet_index(
                    active_offer,
                    SPREADSHEET_ESCALADOS_ID,
                    REPORT_WORKSHEETS[report_type],
                )
                ads_escalados = ads_escalados_spreadsheet.get_worksheet(
                    ads_escalados_worksheet_index
                ).get_all_values()
                sleep(1)

                ads_escalados_to_write_index = search_worksheet_index(
                    active_offer, SPREADSHEET_ESCALADOS_ID, local_date
                )
                is_ads_escalados_date_table_exists = (
                    True if ads_escalados_to_write_index else False
                )
                ads_escalados_current_data = (
                    ads_escalados_spreadsheet.get_worksheet(
                        ads_escalados_to_write_index
                    ).get_all_values()
                    if is_ads_escalados_date_table_exists
                    else None
                )
                sleep(1)
                if not ads_escalados_current_data:
                    print(f"A {active_offer} não possui Ads Escalados.")
                    continue
                if ads_escalados_current_data:
                    ads_current_info = [ads for ads in ads_escalados_current_data[1:-1]]
                    for ad_current_info in ads_current_info:
                        ad_current_info[0] = (
                            "ADV+"
                            if ad_current_info[0] == "CAMPANHAS ADV+ - TOP Ads"
                            else (
                                active_offer
                                if ad_current_info[0]
                                == "TESTE DE VALIDAÇÃO DE CRIATIVO"
                                else ad_current_info[0]
                            )
                        )
                        ad_current_info[3] = currency_to_int(ad_current_info[3])
                    ads_current_info_dict = {
                        linha[0]: linha[3] for linha in ads_current_info
                    }
                for ad in ads_escalados[1:-1]:
                    ad_name = (
                        "ADV+"
                        if ad[0] == "CAMPANHAS ADV+ - TOP Ads"
                        else (
                            active_offer
                            if ad[0] == "TESTE DE VALIDAÇÃO DE CRIATIVO"
                            else ad[0]
                        )
                    )
                    current_budget = (
                        ads_current_info_dict[ad_name]
                        if ads_escalados_current_data
                        else 0
                    )
                    new_sales = 0
                    new_spend = 0
                    new_revenue = 0
                    if ad_name in ads_group:
                        new_spend = sum(
                            [spend[5] for spend in ads_group[ad_name] if spend[5] > 0]
                        )
                        new_sales = sum([sales[1] for sales in ads_group[ad_name]])
                        new_revenue = sum(
                            [
                                revenue[4]
                                for revenue in ads_group[ad_name]
                                if revenue[5] > 0
                            ]
                        )
                        folder = "email-reports"
                        os.makedirs(folder, exist_ok=True)
                        filename = os.path.join(
                            folder, f"{active_offer}_ads_escalados_daily.txt"
                        )
                        with open(filename, "a", encoding="utf-8") as file:
                            file.write(f"O anúncio: {ad_name} - no dia: {local_date}\n")
                            file.write(f"Gastou: {new_spend}\n")
                            file.write(
                                f"Faturou: {new_revenue} - Vendeu: {new_sales}\n"
                            )
                            file.write("-" * 40 + "\n")
                    new_ad_name = (
                        "CAMPANHAS ADV+ - TOP Ads"
                        if ad_name == "ADV+"
                        else (
                            "TESTE DE VALIDAÇÃO DE CRIATIVO"
                            if ad_name == active_offer
                            else ad_name
                        )
                    )
                    ad[0] = new_ad_name
                    ad[3] = current_budget
                    ad[4] = new_spend
                    ad[5] = new_revenue
                    ad[6] = new_sales
                    row = ads_escalados.index(ad) + 1
                    ad[7] = f"=SE(G{row}>0;E{row}/G{row};0)"
                    ad[8] = f"=SE(F{row}>0;F{row}/E{row};0)"
                    ad[9] = local_time

                for formatted_ads in ads_escalados[1:-1]:
                    formatted_ads[3] = int_to_currency(formatted_ads[3])
                    formatted_ads[4] = int_to_currency(formatted_ads[4])
                    formatted_ads[5] = int_to_currency(formatted_ads[5])
                    ads_escalados[-1] = [
                        "AGREGADO",
                        "",
                        "",
                        f"=SOMA(D2:D{row})",  # Total Budget
                        f"=SOMA(E2:E{row})",  # Total Spend
                        f"=SOMA(F2:F{row})",  # Total Revenue
                        f"=SOMA(G2:G{row})",  # Total Sales
                        f"=SE(G{row+1}>0;E{row+1}/G{row+1};0)",  # CPA = Total Spend / Total Sales
                        f"=SE(E{row+1}>0;F{row+1}/E{row+1};0)",  # ROAS = Total Revenue / Total Spend
                        local_time,
                    ]
                ads_escalados_to_write_index = search_worksheet_index(
                    active_offer, SPREADSHEET_ESCALADOS_ID, local_date
                )
                if ads_escalados_to_write_index:
                    ads_escalados_to_write = ads_escalados_spreadsheet.get_worksheet(
                        ads_escalados_to_write_index
                    )
                else:
                    ads_escalados_to_write = duplicate_template_sheet_to_end(
                        spreadsheet=ads_escalados_spreadsheet,
                        template_sheet_index=ads_escalados_worksheet_index,
                        new_sheet_name=local_date,
                    )
                    sleep(1)

                next_row = 1
                ads_escalados_to_write.update(
                    f"A{next_row}:ZZ{next_row + len(ads_escalados) - 1}",
                    ads_escalados,
                    value_input_option="USER_ENTERED",
                )
                sleep(1)
            except Exception as e:
                error_msg = f"Erro ao abrir a planilha {active_offer}: {e}"
                print(error_msg)
                continue

    except Exception as e:
        return ReportResponse(
            report_title="Write ads escalados report - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )


def ads_escalados_report(active_offer: str, report_type: str, period: str):
    raw_local_time = datetime.now(TIMEZONE)
    raw_yesterday = raw_local_time - timedelta(days=1)
    local_time = raw_local_time.strftime("%d/%m/%Y às %Hh%Mmin%Ss")
    local_date = (
        raw_local_time.strftime("%d/%m/%Y")
        if period == "today"
        else raw_yesterday.strftime("%d/%m/%Y")
    )
    try:
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
        all_sales_df = all_sales_df[all_sales_df.columns[[3, 10]]]
        sales_ads_list = all_sales_df.groupby(3).apply(lambda x: x.values.tolist())
        campaigns_spreadsheet = open_spreadsheet(
            DB_SPREADSHEET, DB_SPREADSHEET_FOLDER_ID
        )
        campaigns_worksheet_index = search_worksheet_index(
            DB_SPREADSHEET,
            DB_SPREADSHEET_FOLDER_ID,
            REPORT_TYPE_DATA_WORKSHEETS[report_type],
        )
        campaigns_worksheet = campaigns_spreadsheet.get_worksheet(
            campaigns_worksheet_index
        )
        campaigns = campaigns_worksheet.get_all_values()
        for campaign in campaigns[1:]:
            campaign_id = campaign[3]
            campaign[10] = sales_ads_list[campaign_id][0][1]
        ads_df = pd.DataFrame(campaigns)
        ads_df = ads_df[ads_df.columns[[3, 10, 14, 17, 19, 28]]]
        ads_df[17] = (
            ads_df[17].replace("", "0").astype(str).apply(str_to_int)
        )  # DAILY BUDGET
        ads_df[19] = (
            ads_df[19].replace("", "0").astype(str).apply(str_to_int)
        )  # REVENUE
        ads_df[28] = ads_df[28].replace("", "0").astype(str).apply(str_to_int)  # SPEND
        ads_df[63] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_ad_block)
        )  # AD NAME
        ads_group = ads_df.groupby(63).apply(lambda x: x.values.tolist())
        try:
            ads_escalados_spreadsheet = open_spreadsheet(
                active_offer, SPREADSHEET_ESCALADOS_ID
            )
            ads_escalados_worksheet_index = search_worksheet_index(
                active_offer,
                SPREADSHEET_ESCALADOS_ID,
                REPORT_WORKSHEETS[report_type],
            )
            ads_escalados = ads_escalados_spreadsheet.get_worksheet(
                ads_escalados_worksheet_index
            ).get_all_values()

            ads_escalados_to_write_index = search_worksheet_index(
                active_offer, SPREADSHEET_ESCALADOS_ID, local_date
            )
            is_ads_escalados_date_table_exists = (
                True if ads_escalados_to_write_index else False
            )
            ads_escalados_current_data = (
                ads_escalados_spreadsheet.get_worksheet(
                    ads_escalados_to_write_index
                ).get_all_values()
                if is_ads_escalados_date_table_exists
                else None
            )
            if not ads_escalados_current_data:
                return ReportResponse(
                    report_title="Write ads escalados report - Error",
                    generated_at=datetime.now(),
                    message=f"A {active_offer} não possui Ads Escalados.",
                    status=400,
                )
            if ads_escalados_current_data:
                ads_current_info = [ads for ads in ads_escalados_current_data[1:-1]]
                for ad_current_info in ads_current_info:
                    ad_current_info[0] = (
                        "ADV+"
                        if ad_current_info[0] == "CAMPANHAS ADV+ - TOP Ads"
                        else (
                            active_offer
                            if ad_current_info[0] == "TESTE DE VALIDAÇÃO DE CRIATIVO"
                            else ad_current_info[0]
                        )
                    )
                    ad_current_info[3] = currency_to_int(ad_current_info[3])
                ads_current_info_dict = {
                    linha[0]: linha[3] for linha in ads_current_info
                }
            for ad in ads_escalados[1:-1]:
                ad_name = (
                    "ADV+"
                    if ad[0] == "CAMPANHAS ADV+ - TOP Ads"
                    else (
                        active_offer
                        if ad[0] == "TESTE DE VALIDAÇÃO DE CRIATIVO"
                        else ad[0]
                    )
                )
                current_budget = (
                    ads_current_info_dict[ad_name] if ads_escalados_current_data else 0
                )
                new_sales = 0
                new_spend = 0
                new_revenue = 0
                if ad_name in ads_group:
                    new_spend = sum(
                        [spend[5] for spend in ads_group[ad_name] if spend[5] > 0]
                    )
                    new_sales = sum([sales[1] for sales in ads_group[ad_name]])
                    new_revenue = sum(
                        [revenue[4] for revenue in ads_group[ad_name] if revenue[5] > 0]
                    )
                    folder = "email-reports"
                    os.makedirs(folder, exist_ok=True)
                    filename = os.path.join(
                        folder, f"{active_offer}_ads_escalados_daily.txt"
                    )
                    with open(filename, "a", encoding="utf-8") as file:
                        file.write(f"O anúncio: {ad_name} - no dia: {local_date}\n")
                        file.write(f"Gastou: {new_spend}\n")
                        file.write(f"Faturou: {new_revenue} - Vendeu: {new_sales}\n")
                        file.write("-" * 40 + "\n")
                new_ad_name = (
                    "CAMPANHAS ADV+ - TOP Ads"
                    if ad_name == "ADV+"
                    else (
                        "TESTE DE VALIDAÇÃO DE CRIATIVO"
                        if ad_name == active_offer
                        else ad_name
                    )
                )
                ad[0] = new_ad_name
                ad[3] = current_budget
                ad[4] = new_spend
                ad[5] = new_revenue
                ad[6] = new_sales
                row = ads_escalados.index(ad) + 1
                ad[7] = f"=SE(G{row}>0;E{row}/G{row};0)"
                ad[8] = f"=SE(F{row}>0;F{row}/E{row};0)"
                ad[9] = local_time

            for formatted_ads in ads_escalados[1:-1]:
                formatted_ads[3] = int_to_currency(formatted_ads[3])
                formatted_ads[4] = int_to_currency(formatted_ads[4])
                formatted_ads[5] = int_to_currency(formatted_ads[5])
                ads_escalados[-1] = [
                    "AGREGADO",
                    "",
                    "",
                    f"=SOMA(D2:D{row})",  # Total Budget
                    f"=SOMA(E2:E{row})",  # Total Spend
                    f"=SOMA(F2:F{row})",  # Total Revenue
                    f"=SOMA(G2:G{row})",  # Total Sales
                    f"=SE(G{row+1}>0;E{row+1}/G{row+1};0)",  # CPA = Total Spend / Total Sales
                    f"=SE(E{row+1}>0;F{row+1}/E{row+1};0)",  # ROAS = Total Revenue / Total Spend
                    local_time,
                ]
            ads_escalados_to_write_index = search_worksheet_index(
                active_offer, SPREADSHEET_ESCALADOS_ID, local_date
            )
            if ads_escalados_to_write_index:
                ads_escalados_to_write = ads_escalados_spreadsheet.get_worksheet(
                    ads_escalados_to_write_index
                )
            else:
                ads_escalados_to_write = duplicate_template_sheet_to_end(
                    spreadsheet=ads_escalados_spreadsheet,
                    template_sheet_index=ads_escalados_worksheet_index,
                    new_sheet_name=local_date,
                )
            next_row = 1
            ads_escalados_to_write.update(
                f"A{next_row}:ZZ{next_row + len(ads_escalados) - 1}",
                ads_escalados,
                value_input_option="USER_ENTERED",
            )
        except Exception as e:
            error_msg = f"Erro ao abrir a planilha {active_offer}: {e}"
            print(error_msg)

    except Exception as e:
        return ReportResponse(
            report_title="Write ads escalados report - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )
