from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from routers.todos import obtener_usuario, obtenerDB
from fastapi.testclient import TestClient 
from fastapi import status
import pytest
from models import Todos
SQLALCHEMY_DATABASE_URL="sqlite:///./testdb.db"

engine=create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
                     poolclass= StaticPool )

TestingSessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_obtenerDB():
    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_obtener_usuario():
    return {"nombre_usu": "yo", "id": 1, "rol": "admin"}
app.dependency_overrides[obtenerDB]= override_obtenerDB
app.dependency_overrides[obtener_usuario]=override_obtener_usuario

client=TestClient(app)

@pytest.fixture
def test_todo():
    todo=Todos(
        titulo="aprender",
        descripcion="pues hacer cursos tal",
        prioridad=5,
        dueño_id=1
    )
    db=TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as con:
        con.execute(text("DELETE FROM todos;"))
        con.commit()

def test_leer_autenticados():
    response=client.get("/")
    assert response.status_code == status.HTTP_200_OK

def test_leer_un_autenticado(test_todo):
    response=client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()== {"completada": False, "titulo": "aprender", 
                              "descripcion": "pues hacer cursos tal",
                              "id":1, "prioridad": 5, "dueño_id":1}
    
def test_leer_un_autenticado_not_found(test_todo):
    response=client.get("/todo/99")
    assert response.status_code==status.HTTP_404_NOT_FOUND

def test_crear_todo(test_todo):
    request_data={
        "titulo": "nuevo titulo",
        "descripcion": "nueva desc",
        "prioridad": 5,
        "completada": False,
    }
    response=client.post("/todo/", json=request_data)
    assert response.status_code==201

    db=TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==2).first()
    assert model.titulo==request_data.get("titulo")
    assert model.descripcion==request_data.get("descripcion")
    assert model.completada==request_data.get("completada")
    assert model.prioridad==request_data.get("prioridad")

def test_actualizar_todo(test_todo):
    request_data={
        "titulo": "titulo cambiao",
        "descripcion": "nueva desc",
        "prioridad": 5,
        "completada": False,
    }

    response=client.put("/todo/1", json=request_data)
    assert response.status_code==204
    db = TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==1).first()
    assert model.titulo== "titulo cambiao"

def test_actualizar_todo_not_found(test_todo):
    request_data={
        "titulo": "titulo cambiao",
        "descripcion": "nueva desc",
        "prioridad": 5,
        "completada": False,
    }

    response=client.put("/todo/999", json=request_data)
    assert response.status_code==404

def test_borrar_todo(test_todo):
    response=client.delete("/todo/1")
    assert response.status_code==204
    db=TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==1).first()
    assert model is None

def test_borrar_todo_not_found():
    response=client.delete("/todo/99")
    assert response.status_code==204
    db=TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==1).first()
    assert model is None