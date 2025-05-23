import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config import PROJECT_ID, PRIVATE_KEY_ID, CLIENT_EMAIL, CLIENT_ID, PRIVATE_KEY

credentials_dict = {
    "type": "service_account",
    "project_id": PROJECT_ID,
    "private_key_id": PROJECT_ID,
    "private_key": PRIVATE_KEY,
    "client_email": CLIENT_EMAIL,
    "client_id": CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/conexao-google-sheets%40valiant-student-450820-u3.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}

scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    credentials_dict, scopes=scopes
)

client = gspread.authorize(creds)


def open_spreadsheet(title, folder_id):
    spreadsheet = client.open(title=title, folder_id=folder_id)
    return spreadsheet


def search_worksheet_index(title, folder_id, worksheet_name):
    spreadsheet = open_spreadsheet(title, folder_id)
    page_list = []

    for sheet in spreadsheet.worksheets():
        page_list.append(sheet.title)

    if worksheet_name in page_list:
        return page_list.index(worksheet_name)
    return False


def duplicate_template_sheet_to_end(spreadsheet, template_sheet_index, new_sheet_name):
    template_sheet = spreadsheet.get_worksheet(template_sheet_index)
    new_sheet = template_sheet.duplicate(new_sheet_name=new_sheet_name)
    total_sheets = len(spreadsheet.worksheets())
    spreadsheet.batch_update(
        {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": new_sheet.id, "index": total_sheets},
                        "fields": "index",
                    }
                }
            ]
        }
    )

    return spreadsheet.worksheet(new_sheet_name)
