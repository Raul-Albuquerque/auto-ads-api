import os, pytz
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "x-api-key"
TIMEZONE = pytz.timezone("America/Sao_Paulo")

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME_UTMIFY")
PASSWORD = os.getenv("PASSWORD_UTMIFY")
DASHBOARD_ID = os.getenv("DASHBOARD_ID")

# PLAYER CREDENCIALS
PLAYER_USERNAME = os.getenv("PLAYER_USERNAME")
PLAYER_PASSWORD = os.getenv("PLAYER_PASSWORD")

# EMAIL CREDENCIALS
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# GS CREDENCIALS
PROJECT_ID = os.getenv("PROJECT_ID")
PRIVATE_KEY_ID = os.getenv("PRIVATE_KEY_ID")
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL")
CLIENT_ID = os.getenv("CLIENT_ID")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "").replace("\\n", "\n")

# SPREADSHEETS
DB_SPREADSHEET = os.getenv("DB_SPREADSHEET")
DB_SPREADSHEET_FOLDER_ID = os.getenv("DB_SPREADSHEET_FOLDER_ID")

# DB WORKSHEETS
REPORT_TYPE_DATA_WORKSHEETS = {
    "controle_ads": "RAW",
    "leads": "RAW-CAMPAIGNS",
    "escalados": "RAW-CAMPAIGNS-ESCALADOS",
    "vturb": "Vturb",
}
REPORT_TYPE_FRONT_SALES_WORKSHEETS = {
    "controle_ads": "RAW-SALES",
    "leads": "RAW-CAMPAIGNS-SALES",
    "escalados": "RAW-CAMPAIGNS-ESCALADOS-SALES",
}

# REPORT WORKSHEETS
REPORT_WORKSHEETS = {
    "ads_levas": "Ads (levas)",
    "ads_agregado": "Ads Escalados (Agreg.)",
    "ads_d2d": "Ads Escalados (d2d)",
    "leads": "Modelo",
    "escalados": "MODELO",
}

# SPREADSHEETS PROD
SPREADSHEET_CONTROLE_ADS_ID = os.getenv("SPREADSHEET_CONTROLE_ADS_ID")
SPREADSHEET_LEADS_ID = os.getenv("SPREADSHEET_LEADS_ID")
SPREADSHEET_ESCALADOS_ID = os.getenv("SPREADSHEET_ESCALADOS_ID")

# SPREADSHEETS DEV
# SPREADSHEET_CONTROLE_ADS_ID = os.getenv("DEV_SPREADSHEET_CONTROLE_ADS_ID")
# SPREADSHEET_LEADS_ID = os.getenv("DEV_SPREADSHEET_LEADS_ID")
# SPREADSHEET_ESCALADOS_ID = os.getenv("DEV_SPREADSHEET_ESCALADOS_ID")
