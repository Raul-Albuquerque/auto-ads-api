from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health")
def get_api_router():
  return {"Message": "The API is running!" }