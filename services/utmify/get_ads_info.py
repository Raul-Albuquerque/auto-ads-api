import requests, os, math, logging
from dotenv import load_dotenv

from core.helpers import get_date, generate_basic_token
from models.report_models import ReportResponse
from datetime import datetime

load_dotenv(override=True)

# Configurando logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base_url = os.getenv("BASE_URL")
username = os.getenv("USERNAME_UTMIFY")
password = os.getenv("PASSWORD_UTMIFY")
dashboard_id = os.getenv("DASHBOARD_ID")

def auth():
    url = f"{base_url}/users/auth"
    basic_token = generate_basic_token(username=username, password=f"{password}#")
    headers = {"Authorization": basic_token}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Levanta um erro se o status for 4xx ou 5xx

        token = response.json().get("auth", {}).get("token")
        if not token:
            logger.error("Erro na autenticação: Token não encontrado na resposta")
            raise ValueError("Token não encontrado na resposta da API")
        
        logger.info("Autenticação bem-sucedida")
        return token

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na autenticação: {e}")
        raise  # Propaga a exceção para ser tratada no nível superior

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
            "dateRange": {"from": start_date, "to": end_date},
            "nameContains": name_contains,
            "productNames": products
        }

        logger.info(f"Enviando requisição para {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Payload: {payload}")

        response = requests.post(url, json=payload, headers=headers, timeout=15)
        logger.info(f"Resposta da API - Status Code: {response.status_code}")

        # Verifica se o status é erro antes de tentar processar a resposta
        response.raise_for_status()

        try:
            data = response.json().get("results", [])
        except ValueError:
            logger.error("Erro ao converter resposta para JSON")
            raise ValueError("A resposta da API não está em formato JSON válido")

        logger.info(f"Total de campanhas encontradas: {len(data)}")

        for item in data:
            item.pop('approvedOrdersByProductId', None)

        return ReportResponse(
            report_title="Get Utmify Ads - Success",
            generated_at=datetime.now(),
            count=len(data),
            data=data,
            status=200
        )

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Erro HTTP: {http_err}")
        return ReportResponse(report_title="Get Utmify Ads - Error", generated_at=datetime.now(), message=f"Erro HTTP: {str(http_err)}", status=400)

    except requests.exceptions.RequestException as req_err:
        logger.error(f"Erro de requisição: {req_err}")
        return ReportResponse(report_title="Get Utmify Ads - Error", generated_at=datetime.now(), message=f"Erro na requisição: {str(req_err)}", status=400)

    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return ReportResponse(report_title="Get Utmify Ads - Error", generated_at=datetime.now(), message=f"Erro inesperado: {str(e)}", status=400)
