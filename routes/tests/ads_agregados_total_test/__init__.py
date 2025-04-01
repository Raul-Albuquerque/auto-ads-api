from .ads_total_report import router as ads_total_router
from .offer_total_report import router as offer_total_router

ads_total_router.include_router(offer_total_router)