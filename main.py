from fastapi import FastAPI

from routes import utmify_router, report_router

app = FastAPI()

app.include_router(utmify_router)
app.include_router(report_router)