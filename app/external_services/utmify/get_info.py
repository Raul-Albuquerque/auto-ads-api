import requests, os, logging
from datetime import datetime

from app.core.helpers import get_date, generate_basic_token
from app.models.report_model import ReportResponse
from config import BASE_URL, USERNAME, PASSWORD, DASHBOARD_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def auth():
    url = f"{BASE_URL}/users/auth"
    basic_token = generate_basic_token(username=USERNAME, password=f"{PASSWORD}")
    headers = {"Authorization": basic_token}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        token = response.json().get("auth", {}).get("token")
        if not token:
            logger.error("Erro na autenticação: Token não encontrado na resposta")
            raise ValueError("Token não encontrado na resposta da API")

        logger.info("Autenticação bem-sucedida")
        return token

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na autenticação: {e}")
        raise


def get_data(
    day: str, level: str, ad_plataform: str, name_contains=None, products=None
):
    url = (
        f"{BASE_URL}/orders/search-objects"
        if ad_plataform == "meta"
        else f"{BASE_URL}/orders/search-objects/google"
    )

    try:
        token = auth()
        start_date = get_date(day=day, period="start")
        end_date = get_date(day=day, period="end")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = (
            {
                "level": level,
                "adObjectStatuses": None,
                "metaAdAccountIds": None,
                "orderBy": "greater_profit",
                "dashboardId": DASHBOARD_ID,
                "dateRange": {"from": start_date, "to": end_date},
                "nameContains": name_contains,
                "productNames": products,
            }
            if ad_plataform == "meta"
            else {
                "level": level,
                "adAccountIds": None,
                "orderBy": "greater_profit",
                "dashboardId": DASHBOARD_ID,
                "dateRange": {"from": start_date, "to": end_date},
                "nameContains": name_contains,
                "productNames": products,
                "status": None,
            }
        )

        logger.info(f"Enviando requisição para {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Payload: {payload}")

        response = requests.post(url, json=payload, headers=headers, timeout=15)
        logger.info(f"Resposta da API - Status Code: {response.status_code}")

        response.raise_for_status()

        try:
            data = response.json().get("results", [])
        except ValueError:
            logger.error("Erro ao converter resposta para JSON")
            raise ValueError("A resposta da API não está em formato JSON válido")

        logger.info(f"Total de ocorrências encontradas: {len(data)}")

        for item in data:
            item.pop("approvedOrdersByProductId", None)

        return ReportResponse(
            report_title="Get Utmify Data - Success",
            generated_at=datetime.now(),
            count=len(data),
            data=data,
            status=200,
        )

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Erro HTTP: {http_err}")
        return ReportResponse(
            report_title="Get Utmify Data - Error",
            generated_at=datetime.now(),
            message=f"Erro HTTP: {str(http_err)}",
            status=400,
        )

    except requests.exceptions.RequestException as req_err:
        logger.error(f"Erro de requisição: {req_err}")
        return ReportResponse(
            report_title="Get Utmify Data - Error",
            generated_at=datetime.now(),
            message=f"Erro na requisição: {str(req_err)}",
            status=400,
        )

    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return ReportResponse(
            report_title="Get Utmify Data - Error",
            generated_at=datetime.now(),
            message=f"Erro inesperado: {str(e)}",
            status=400,
        )
