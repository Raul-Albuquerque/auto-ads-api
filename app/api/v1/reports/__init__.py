from fastapi import APIRouter

from .write_ads_levas import router as write_ads_levas_router
from .write_ads_agregado import router as write_ads_agregado_router
from .write_ads_d2d import router as write_ads_d2d_routers
from .write_leads import router as write_leads_router
from .write_escalados import router as write_escalados_router

report_router = APIRouter()

report_router.include_router(write_ads_levas_router)
report_router.include_router(write_ads_agregado_router)
report_router.include_router(write_ads_d2d_routers)
report_router.include_router(write_leads_router)
report_router.include_router(write_escalados_router)
