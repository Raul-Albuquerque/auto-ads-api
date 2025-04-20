from fastapi import APIRouter

from .data import data_router

api_v1_router = APIRouter()

api_v1_router.include_router(data_router, prefix="/data")
