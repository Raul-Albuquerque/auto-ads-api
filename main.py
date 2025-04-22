from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import utmify_router, report_router, health_router, test_router

from app.api.v1 import api_v1_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(utmify_router)
app.include_router(report_router)
app.include_router(health_router)
app.include_router(test_router)

app.include_router(api_v1_router, prefix="/api/v1")
