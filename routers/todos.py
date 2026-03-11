from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path, APIRouter
from starlette import status
from pydantic import BaseModel, Field
from models import Todos
from database import SessionLocal
from .auth import obtener_usuario
router = APIRouter()

def obtenerDB():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session, Depends(obtenerDB)]
user_dependency=Annotated[dict, Depends(obtener_usuario)]

class SolicitudTodo(BaseModel):
    titulo:str=Field(min_length=3)
    descripcion:str=Field(min_length=3, max_length=100)
    prioridad:int=Field(gt=0, lt=6)
    completada:bool

@router.get("/", status_code=status.HTTP_200_OK)
async def leerDatos(usuario: user_dependency, db: db_dependency):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Autenticacion fallida")
    return db.query(Todos).filter(Todos.dueño_id==usuario.get("id")).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def datosPorId(usuario:user_dependency, db: db_dependency, todo_id: int=Path(gt=0)):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Autenticacion fallida")
    todo_model=db.query(Todos).filter(Todos.id==todo_id).filter(Todos.dueño_id==usuario.get("id")).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="No encontrado")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def crear_Todo(usuario:user_dependency, db:db_dependency, solicitud:SolicitudTodo):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Autenticacion fallida")
    todo_model=Todos(**solicitud.dict(), dueño_id=usuario.get("id"))

    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizarTodo(usuario: user_dependency, db: db_dependency, solicitud:SolicitudTodo, todo_id:int=Path(gt=0)):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Autenticacion fallida")
    todo_model=db.query(Todos).filter(Todos.id==todo_id).filter(Todos.dueño_id==usuario.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="no se encuentra la tarea")
    todo_model.titulo=solicitud.titulo
    todo_model.descripcion=solicitud.descripcion
    todo_model.prioridad=solicitud.prioridad
    todo_model.completada=solicitud.completada
    db.add(todo_model)
    db.commit()
    
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrarTodo(usuario: user_dependency, db: db_dependency, todo_id:int = Path(gt=0)):
    if usuario is None:
        raise HTTPException(status_code=401, detail="Autenticacion fallida")
    todo_model=db.query(Todos).filter(Todos.id==todo_id).filter(Todos.dueño_id==usuario.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="no se encuentra la tarea")
    db.query(Todos).filter(Todos.id==todo_id).delete()
    db.commit()