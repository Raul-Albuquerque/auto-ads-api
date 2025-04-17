from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

from services.api_request import call_until_success

endpoints = [
    "https://automacao-nkh9m.ondigitalocean.app/utmify/campaigns/escalados/today",
    "https://automacao-nkh9m.ondigitalocean.app/utmify/campaigns/escalados/sales/today",
    "https://automacao-nkh9m.ondigitalocean.app/test/ads/escalados/daily"
]

# Função que será chamada pelo agendador
async def run_scheduled_job():
    print("Executando job automático...")
    resultados = []
    for endpoint in endpoints:
        resultado = await call_until_success(endpoint)
        resultados.append(resultado)
    print("Resultado do job automático:", resultados)

# Wrapper porque APScheduler só aceita funções síncronas no `add_job`
def schedule_job():
    asyncio.create_task(run_scheduled_job())

# Configura o agendador
scheduler = AsyncIOScheduler()

# Roda a cada 2h das 8h até 00h
scheduler.add_job(schedule_job, CronTrigger(hour=2, minute=55))

scheduler.start()
