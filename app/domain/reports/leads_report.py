import os
from datetime import datetime, timedelta
import pandas as pd

from app.models.report_model import ReportResponse
from app.static_data.active_offers_info import ACTIVE_OFFERS_INFO
from app.core.helpers import (
    deduplicate_leads_group,
    groupy_leads,
    ungroup_leads,
)
from app.core.cleaners import (
    extract_lead_info,
    extract_lead_block,
    extract_ad_block,
    extract_ad_lead,
)
from app.core.numbers_manipulators import currency_to_int, str_to_int, int_to_currency
from app.external_services.google_sheets import (
    open_spreadsheet,
    search_worksheet_index,
    duplicate_template_sheet_to_end,
)
from config import (
    TIMEZONE,
    DB_SPREADSHEET,
    DB_SPREADSHEET_FOLDER_ID,
    REPORT_TYPE_DATA_WORKSHEETS,
    REPORT_TYPE_FRONT_SALES_WORKSHEETS,
    SPREADSHEET_LEADS_ID,
    REPORT_WORKSHEETS,
)


def all_leads_report(report_type: str, period: str):
    raw_local_time = (
        datetime.now(TIMEZONE) - timedelta(days=1)
        if period == "yesterday"
        else datetime.now(TIMEZONE)
    )
    local_date = raw_local_time.strftime("%d/%m/%Y")

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
        ads_df = ads_df[ads_df.columns[[3, 10, 14, 19, 28]]]
        ads_df[19] = (
            ads_df[19].replace("", "0").astype(str).apply(str_to_int)
        )  # REVENUE
        ads_df[28] = ads_df[28].replace("", "0").astype(str).apply(str_to_int)  # SPEND
        ads_df[62] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_lead_info)
        )  # FULL LEAD NAME
        ads_df[63] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_lead_block)
        )  # LEAD
        ads_df[64] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_ad_block)
        )  # AD NAME
        ads_df[65] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_ad_lead)
        )  # LEAD + ADNAME
        raw_leads_info_group = ads_df.groupby(63).apply(lambda x: x.values.tolist())
        leads_info_group = deduplicate_leads_group(raw_leads_info_group)

        for active_offer_item in ACTIVE_OFFERS_INFO:
            active_offer = active_offer_item["offer_name"]
            try:
                leads_spreadsheet = open_spreadsheet(active_offer, SPREADSHEET_LEADS_ID)
                leads_worksheet_index = search_worksheet_index(
                    active_offer, SPREADSHEET_LEADS_ID, REPORT_WORKSHEETS[report_type]
                )
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
                    print("_" * 50)
                    new_sales_amount = 0
                    new_spend_amount = 0
                    new_revenue_amount = 0
                    for ad in lead[7:]:
                        ad_name = ad[1]
                        ad[2] = currency_to_int(ad[2])  # spend
                        ad[3] = currency_to_int(ad[3])  # revenue
                        ad[4] = str_to_int(ad[4])  # sales
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
                            new_roas = (
                                new_revenue / new_spend
                                if new_revenue > 0 and new_spend > 0
                                else 0
                            )
                            new_arpu = (
                                int(new_revenue / new_sales) if new_sales > 0 else 0
                            )

                            folder = "email-reports"
                            os.makedirs(folder, exist_ok=True)
                            filename = os.path.join(
                                folder, f"{active_offer}_LEADS_DAILY.txt"
                            )
                            with open(filename, "a", encoding="utf-8") as file:
                                file.write(
                                    f"O anúncio: {ad_name} - na Lead: {lead_name}\n"
                                )
                                file.write(f"Gastos UTMify: {new_spend}\n")
                                file.write(f"Faturamento UTMify: {new_revenue}\n")
                                file.write(f"Vendas UTMIfy: {new_sales}\n")
                                file.write(
                                    f"Novo CPA: {new_cpa} - Novo ROAS: {round(new_roas,2)} - Novo ARPU: {new_arpu}\n"
                                )
                                file.write("-" * 40 + "\n")

                        ad[2] = int_to_currency(new_spend)
                        ad[3] = int_to_currency(new_revenue)
                        ad[4] = new_sales
                        ad[5] = int_to_currency(new_cpa)
                        ad[6] = round(new_roas, 2)
                        ad[7] = int_to_currency(new_arpu)

                    new_spend_amount = sum([item[2] for item in lead[7:]])
                    new_revenue_amount = sum([item[3] for item in lead[7:]])
                    new_sales_amount = sum([item[4] for item in lead[7:]])
                    new_cpa_amount = (
                        int(new_spend_amount / new_sales_amount)
                        if new_sales_amount > 0
                        else 0
                    )
                    new_roas_amount = (
                        new_revenue_amount / new_spend_amount
                        if new_revenue_amount > 0 and new_spend_amount > 0
                        else 0
                    )
                    new_arpu_amount = (
                        int(new_revenue_amount / new_sales_amount)
                        if new_sales_amount > 0
                        else 0
                    )
                    lead[4][:] = [
                        "",
                        "",
                        int_to_currency(new_spend_amount * 100),
                        int_to_currency(new_revenue_amount * 100),
                        new_sales_amount,
                        new_cpa_amount,
                        round(new_roas_amount, 2),
                        int_to_currency(new_arpu_amount),
                    ]

            daily_lead_info = ungroup_leads(leads_group)
            daily_lead_worksheet_index = search_worksheet_index(
                active_offer, SPREADSHEET_LEADS_ID, local_date
            )
            if daily_lead_worksheet_index:
                daily_lead_worksheet = leads_spreadsheet.get_worksheet(
                    daily_lead_worksheet_index
                )
                # daily_lead_worksheet.clear()
            else:
                daily_lead_worksheet = duplicate_template_sheet_to_end(
                    spreadsheet=leads_spreadsheet,
                    template_sheet_index=leads_worksheet_index,
                    new_sheet_name=local_date,
                )
                # daily_lead_worksheet.clear()
            next_row = 1
            daily_lead_worksheet.update(
                f"A{next_row}:ZZ{next_row + len(daily_lead_info) - 1}", daily_lead_info
            )
        return ReportResponse(
            report_title="Daily Leads report function - Success",
            generated_at=datetime.now(),
            message=f"Função executada com sucesso!",
            status=200,
        )

    except Exception as e:
        return ReportResponse(
            report_title="Write leads report - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )


def leads_report(report_type: str, period: str, active_offer: str):
    raw_local_time = (
        datetime.now(TIMEZONE) - timedelta(days=1)
        if period == "yesterday"
        else datetime.now(TIMEZONE)
    )
    local_date = raw_local_time.strftime("%d/%m/%Y")

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
        ads_df = ads_df[ads_df.columns[[3, 10, 14, 19, 28]]]
        ads_df[19] = (
            ads_df[19].replace("", "0").astype(str).apply(str_to_int)
        )  # REVENUE
        ads_df[28] = ads_df[28].replace("", "0").astype(str).apply(str_to_int)  # SPEND
        ads_df[62] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_lead_info)
        )  # FULL LEAD NAME
        ads_df[63] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_lead_block)
        )  # LEAD
        ads_df[64] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_ad_block)
        )  # AD NAME
        ads_df[65] = (
            ads_df[14].replace("", "0").astype(str).apply(extract_ad_lead)
        )  # LEAD + ADNAME
        raw_leads_info_group = ads_df.groupby(63).apply(lambda x: x.values.tolist())
        leads_info_group = deduplicate_leads_group(raw_leads_info_group)
        try:
            leads_spreadsheet = open_spreadsheet(active_offer, SPREADSHEET_LEADS_ID)
            leads_worksheet_index = search_worksheet_index(
                active_offer, SPREADSHEET_LEADS_ID, REPORT_WORKSHEETS[report_type]
            )
            leads_worksheet = leads_spreadsheet.get_worksheet(leads_worksheet_index)
        except Exception as e:
            error_msg = f"Erro ao abrir a planilha {active_offer}: {e}"
            print(error_msg)
        all_leads = leads_worksheet.get_all_values()
        leads_group = groupy_leads(all_leads)
        for lead in leads_group:
            lead_name = lead[1][1]
            if lead_name in leads_info_group:
                print(f"a {lead_name} teve ocorrência na lista")
                print("_" * 50)
                new_sales_amount = 0
                new_spend_amount = 0
                new_revenue_amount = 0
                for ad in lead[7:]:
                    ad_name = ad[1]
                    ad[2] = currency_to_int(ad[2])  # spend
                    ad[3] = currency_to_int(ad[3])  # revenue
                    ad[4] = str_to_int(ad[4])  # sales
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
                        new_roas = (
                            new_revenue / new_spend
                            if new_revenue > 0 and new_spend > 0
                            else 0
                        )
                        new_arpu = int(new_revenue / new_sales) if new_sales > 0 else 0

                        folder = "email-reports"
                        os.makedirs(folder, exist_ok=True)
                        filename = os.path.join(
                            folder, f"{active_offer}_LEADS_DAILY.txt"
                        )
                        with open(filename, "a", encoding="utf-8") as file:
                            file.write(f"O anúncio: {ad_name} - na Lead: {lead_name}\n")
                            file.write(f"Gastos UTMify: {new_spend}\n")
                            file.write(f"Faturamento UTMify: {new_revenue}\n")
                            file.write(f"Vendas UTMIfy: {new_sales}\n")
                            file.write(
                                f"Novo CPA: {new_cpa} - Novo ROAS: {round(new_roas,2)} - Novo ARPU: {new_arpu}\n"
                            )
                            file.write("-" * 40 + "\n")

                    ad[2] = int_to_currency(new_spend)
                    ad[3] = int_to_currency(new_revenue)
                    ad[4] = new_sales
                    ad[5] = int_to_currency(new_cpa)
                    ad[6] = round(new_roas, 2)
                    ad[7] = int_to_currency(new_arpu)

                new_spend_amount = sum([item[2] for item in lead[7:]])
                new_revenue_amount = sum([item[3] for item in lead[7:]])
                new_sales_amount = sum([item[4] for item in lead[7:]])
                new_cpa_amount = (
                    int(new_spend_amount / new_sales_amount)
                    if new_sales_amount > 0
                    else 0
                )
                new_roas_amount = (
                    new_revenue_amount / new_spend_amount
                    if new_revenue_amount > 0 and new_spend_amount > 0
                    else 0
                )
                new_arpu_amount = (
                    int(new_revenue_amount / new_sales_amount)
                    if new_sales_amount > 0
                    else 0
                )
                lead[4][:] = [
                    "",
                    "",
                    int_to_currency(new_spend_amount * 100),
                    int_to_currency(new_revenue_amount * 100),
                    new_sales_amount,
                    new_cpa_amount,
                    round(new_roas_amount, 2),
                    int_to_currency(new_arpu_amount),
                ]

        daily_lead_info = ungroup_leads(leads_group)
        daily_lead_worksheet_index = search_worksheet_index(
            active_offer, SPREADSHEET_LEADS_ID, local_date
        )
        if daily_lead_worksheet_index:
            daily_lead_worksheet = leads_spreadsheet.get_worksheet(
                daily_lead_worksheet_index
            )
            # daily_lead_worksheet.clear()
        else:
            daily_lead_worksheet = duplicate_template_sheet_to_end(
                spreadsheet=leads_spreadsheet,
                template_sheet_index=leads_worksheet_index,
                new_sheet_name=local_date,
            )
            # daily_lead_worksheet.clear()
        next_row = 1
        daily_lead_worksheet.update(
            f"A{next_row}:ZZ{next_row + len(daily_lead_info) - 1}", daily_lead_info
        )
        return ReportResponse(
            report_title="Daily Leads report function - Success",
            generated_at=datetime.now(),
            message=f"Função executada com sucesso!",
            status=200,
        )

    except Exception as e:
        return ReportResponse(
            report_title="Write leads report - Error",
            generated_at=datetime.now(),
            message=f"Error: {str(e)}",
            status=400,
        )
