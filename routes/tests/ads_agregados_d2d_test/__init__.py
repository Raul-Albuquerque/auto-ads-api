from .ads_d2d_report import router as ads_d2d_router
from .ads_d2d_offer_report import router as ads_d2d_router_offer

ads_d2d_router.include_router(ads_d2d_router_offer)