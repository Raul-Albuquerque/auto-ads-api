from fastapi import APIRouter

from .utmify import utmify_router

data_router = APIRouter()

data_router.include_router(utmify_router)
