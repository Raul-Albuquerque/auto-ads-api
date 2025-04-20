from fastapi import APIRouter

from .write_ads_levas import router as write_ads_levas_router
from .write_ads_agregado import router as write_ads_agregado_router

report_router = APIRouter()

report_router.include_router(write_ads_levas_router)
report_router.include_router(write_ads_agregado_router)
