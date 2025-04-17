from fastapi import APIRouter

from services.api_request import call_until_success

router = APIRouter()

endpoints = [
  "https://automacao-nkh9m.ondigitalocean.app/utmify/campaigns/escalados/today",
  "https://automacao-nkh9m.ondigitalocean.app/utmify/campaigns/escalados/sales/today",
  "https://automacao-nkh9m.ondigitalocean.app/test/ads/escalados/daily"
]

@router.get("/write/ads/report")
async def write_ads_escalados_report():
  resultados = []
  for endpoint in endpoints:
    resultado = await call_until_success(endpoint)
    resultados.append(resultado)

  return {"resumo": resultados}