import requests, os, math
from dotenv import load_dotenv

from core.helpers import get_date, generate_basic_token
from models.report_models import ReportResponse
from models.front_products_list import front_products_list
import numpy as np
from datetime import datetime

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

def get_campaigns(day, name_contains=None, products=None):
  url = f"{base_url}/orders/search-objects"
  try:
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
      "productNames": products
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json().get("results", [])
    for item in data:
      item.pop('approvedOrdersByProductId', None)
      
    return ReportResponse(report_title="Get Utmify Ads - Success", generated_at=datetime.now(), count=len(data), data=data, status=200)
    
  except Exception as e:
    return ReportResponse(report_title="Get Utmify Ads - Error", generated_at=datetime.now(), message=f"Error: {str(e)}", status=400)


