from fastapi import APIRouter, HTTPException
import asyncio

health_router = APIRouter()


@health_router.get("/health", status_code=200)
async def check_health():
    # Simulando uma verificação de dependência (ex: banco de dados)
    try:
        await asyncio.sleep(0.1)  # Simula latência de conexão com o DB
        return {"status": "ok", "message": "The API is healthy!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
