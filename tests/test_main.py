from fastapi.testclient import TestClient

def test_read_main(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API funcionando correctamente"}

def test_docs_exist(client: TestClient):
    response = client.get("/docs")
    assert response.status_code == 200

# Añadimos un test básico de manejo de endpoints inexistentes
def test_404_not_found(client: TestClient):
    response = client.get("/this/does/not/exist")
    assert response.status_code == 404
