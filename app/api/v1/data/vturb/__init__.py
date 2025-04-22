from fastapi import APIRouter

from .write_player_stats import router as get_player_stats_router

vturb_router = APIRouter()

vturb_router.include_router(get_player_stats_router)
