from fastapi import APIRouter

from .write_utmify_data import router as write_utmify_data_router
from .write_utmify_front_sales import router as write_utmify_front_sales_router

utmify_router = APIRouter()

utmify_router.include_router(write_utmify_data_router)
utmify_router.include_router(write_utmify_front_sales_router)
