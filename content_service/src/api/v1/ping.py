from fastapi import APIRouter, Depends
from dependencies import get_current_principal

router = APIRouter()

@router.get("/ping")
async def ping(principal = Depends(get_current_principal)):
    return {"principal": principal}