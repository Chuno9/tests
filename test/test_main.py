from fastapi.testclient import TestClient
import p4.TodoApp.main2 as main2
from fastapi import status

client=TestClient(main2.app)

def test_health():
    response=client.get("/healthy")
    assert response.status_code==status.HTTP_200_OK
    assert response.json()=={"status": "healthy"}
