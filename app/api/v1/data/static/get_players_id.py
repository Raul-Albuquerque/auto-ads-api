from fastapi import APIRouter

from app.static_data import PLAYERS_BY_OFFER

router = APIRouter()


@router.get("/players_id")
def get_active_offers():
    all_ids = [player_id for ids in PLAYERS_BY_OFFER.values() for player_id in ids]
    return all_ids
