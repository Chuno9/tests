from fastapi import Depends, HTTPException, Path, APIRouter

router=APIRouter()

@router.get("/auth/")
async def get_usuario():
    return {"usuario": "Autenticado"}