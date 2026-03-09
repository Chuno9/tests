from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path, APIRouter
from starlette import status
from pydantic import BaseModel, Field
from database import SessionLocal
from models import Usuarios
from passlib.context import CryptContext

router=APIRouter()

bcrypt_context=CryptContext(schemes=['bcrypt'], deprecated='auto')

class SolicitudUsuario(BaseModel):
    nombreUsu:str
    email:str
    nombre:str
    apellido:str
    contraseña:str
    rol:str

def obtenerDB():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session, Depends(obtenerDB)]

@router.post("/auth/", status_code=status.HTTP_201_CREATED)
async def crear_usuario(db: db_dependency, usuario :SolicitudUsuario):
    usuario=Usuarios(
        email=usuario.email,
        nombreUsu=usuario.nombreUsu,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        hash_password=bcrypt_context.hash(usuario.contraseña),
        rol=usuario.rol,
        activo=True
    )
    db.add(usuario)
    db.commit()