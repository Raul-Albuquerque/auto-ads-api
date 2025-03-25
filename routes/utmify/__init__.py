from .get_all_ads import router as utmify_router
from .get_all_front_sales import router as all_sales_utmify_router

utmify_router.include_router(all_sales_utmify_router)