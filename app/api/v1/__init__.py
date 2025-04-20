from fastapi import APIRouter

from .data import data_router
from .health import health_router

api_v1_router = APIRouter()

api_v1_router.include_router(data_router, prefix="/data")
api_v1_router.include_router(health_router)
