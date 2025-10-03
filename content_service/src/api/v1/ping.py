from fastapi import APIRouter, Depends
from dependencies import get_current_principal

router = APIRouter()


@router.get("")
async def ping(principal=Depends(get_current_principal)):
    # principal может быть либо "guest", либо dict
    if principal == "guest":
        return {"principal": "guest"}
    return {"principal": principal}
