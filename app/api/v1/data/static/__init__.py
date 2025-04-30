from fastapi import APIRouter

from .get_active_offers import router as active_offers_router
from .get_players_id import router as players_id_router

static_router = APIRouter()

static_router.include_router(active_offers_router)
static_router.include_router(players_id_router)
