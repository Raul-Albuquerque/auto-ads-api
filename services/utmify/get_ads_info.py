import requests, os
from dotenv import load_dotenv

from core.helpers import get_date, generate_basic_token
from models.front_products_list import products_list

load_dotenv(override=True)

base_url = os.getenv("BASE_URL")
username = os.getenv("USERNAME_UTMIFY")
password = os.getenv("PASSWORD_UTMIFY")
dashboard_id = os.getenv("DASHBOARD_ID")

def auth():
  url = f"{base_url}/users/auth"
  basic_token = generate_basic_token(username=username, password=password)
  headers = {
    "Authorization": basic_token
  }

  response = requests.get(url, headers=headers)
  token = response.json().get("auth").get("token")
  return token

def get_campaigns(day, name_contains=None):
  url = f"{base_url}/orders/search-objects"
  token = auth()
  start_date = get_date(day=day, period="start")
  end_date = get_date(day=day, period="end")

  headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
  }

  payload = {
    "level": "ad",
    "adObjectStatuses": None,
    "metaAdAccountIds": None,
    "orderBy": "greater_profit",
    "dashboardId": dashboard_id,
    "dateRange": {
      "from": start_date,
      "to": end_date
    },
    "nameContains": name_contains,
    "productNames": products_list
  }
  response = requests.post(url, json=payload, headers=headers)
  response.raise_for_status()

  return response.json()
