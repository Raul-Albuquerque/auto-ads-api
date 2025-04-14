from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import utmify_router, report_router,health_router,test_router, vturb_router

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  
  allow_credentials=True,
  allow_methods=["GET"],
  allow_headers=["*"],  
)

app.include_router(utmify_router)
app.include_router(report_router)
app.include_router(health_router)
app.include_router(test_router)
app.include_router(vturb_router)