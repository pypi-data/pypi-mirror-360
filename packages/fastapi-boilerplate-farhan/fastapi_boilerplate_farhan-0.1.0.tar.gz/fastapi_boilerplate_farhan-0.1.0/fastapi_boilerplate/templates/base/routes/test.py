from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["test"])

@router.get("/ping")
async def ping():
    return {"ping": "pong"}
