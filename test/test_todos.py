from routers.todos import obtener_usuario, obtenerDB
from fastapi import status
from models import Todos
from .utils import *
app.dependency_overrides[obtenerDB]= override_obtenerDB
app.dependency_overrides[obtener_usuario]=override_obtener_usuario


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
    assert response.status_code==404