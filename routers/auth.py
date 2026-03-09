from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path, APIRouter
from starlette import status
from pydantic import BaseModel, Field
from database import SessionLocal
from models import Usuarios
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router=APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY='21b534a9eab568d77916c8933e701f84509fa8fce038f0b35932546fb3babdb3'
ALGORITHM='HS256'

bcrypt_context=CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer=OAuth2PasswordBearer(tokenUrl="auth/token")

class SolicitudUsuario(BaseModel):
    nombreUsu:str
    email:str
    nombre:str
    apellido:str
    contraseña:str
    rol:str

class Token(BaseModel):
    acces_token:str
    token_type:str

def obtenerDB():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session, Depends(obtenerDB)]

def autenticacion_usuario(nombreUsu:str, contraseña:str, db):
    usuario=db.query(Usuarios).filter(Usuarios.nombreUsu == nombreUsu).first()
    if not usuario:
        return False
    if not bcrypt_context.verify(contraseña, usuario.hash_password):
        return False
    return usuario

def crear_token(nombreUsu:str, id_usu:int,expires_delta:timedelta):

    encode = {"sub": nombreUsu, "id": id_usu}
    expires=datetime.now(timezone.utc) + expires_delta
    encode.update({"exp":expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def obtener_usuario(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nombreUsu: str = payload.get("sub")
        id_usu: int = payload.get("id")
        if nombreUsu is None or id_usu is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tienes acceso a estos recursos")
        return{"nombreUsu": nombreUsu, "id": id_usu} 
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tienes acceso a estos recursos")
@router.post("/", status_code=status.HTTP_201_CREATED)
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

@router.post("/token", response_model=Token)
async def acces_token(form_data : Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    usuario= autenticacion_usuario(form_data.username, form_data.password, db)
    if not usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tienes acceso a estos recursos")
    token= crear_token(usuario.nombreUsu, usuario.id, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}