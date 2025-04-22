from fastapi import APIRouter

from .utmify import utmify_router
from .vturb import vturb_router

data_router = APIRouter()

data_router.include_router(utmify_router)
data_router.include_router(vturb_router)
