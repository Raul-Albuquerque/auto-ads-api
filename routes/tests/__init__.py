from .ads_levas_test import test_router
from .total_aggregate_test import ads_total_router

test_router.include_router(ads_total_router)