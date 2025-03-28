from .levas_report import router as test_router
from .offer_levas_report import router as offer_levas_router

test_router.include_router(offer_levas_router)