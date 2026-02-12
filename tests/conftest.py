from fastapi.testclient import TestClient
import pytest
from main import app

@pytest.fixture
def client():
    # En proyectos reales, aquí se inicializaría una base de datos de test
    # y se sobrescribirían las dependencias.
    # Por ahora, usamos el cliente tal cual para pruebas de integración o unitarias
    # donde se mockeen los servicios.
    with TestClient(app) as client:
        yield client
