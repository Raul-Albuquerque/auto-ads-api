from fastapi import APIRouter

from .write_utmify_data import router as write_utmify_data_router

utmify_router = APIRouter()

utmify_router.include_router(write_utmify_data_router)
