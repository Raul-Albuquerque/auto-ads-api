from fastapi import APIRouter

from app.static_data import ACTIVE_OFFERS_INFO

router = APIRouter()


@router.get("/active_offers")
def get_active_offers():
    offers = [item["offer_name"] for item in ACTIVE_OFFERS_INFO]
    return offers
