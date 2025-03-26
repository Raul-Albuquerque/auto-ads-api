from .ads_levas_report import router as report_router
from .ads_levas_report_test import router as report_router_test

report_router.include_router(report_router_test)