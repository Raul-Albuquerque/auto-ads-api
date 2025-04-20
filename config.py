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

# SPREADSHEETS
DB_SPREADSHEET = os.getenv("DB_SPREADSHEET")
DB_SPREADSHEET_FOLDER_ID = os.getenv("DB_SPREADSHEET_FOLDER_ID")

# GS CREDENCIALS
PROJECT_ID = os.getenv("PROJECT_ID")
PRIVATE_KEY_ID = os.getenv("PRIVATE_KEY_ID")
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL")
CLIENT_ID = os.getenv("CLIENT_ID")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "").replace("\\n", "\n")

# DB WORKSHEETS
REPORT_TYPE_DATA_WORKSHEETS = {
    "controle_ads": "RAW",
    "leads": "RAW-CAMPAIGNS",
    "escalados": "RAW-CAMPAIGNS-ESCALADOS",
}
REPORT_TYPE_FRONT_SALES_WORKSHEETS = {
    "controle_ads": "RAW-SALES",
    "leads": "RAW-CAMPAIGNS-SALES",
    "escalados": "RAW-CAMPAIGNS-ESCALADOS-SALES",
}
