from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_system_resources_endpoint():
    response = client.get("/system/resources")
    assert response.status_code == 200
    data = response.json()
    
    # Check CPU structure
    assert "cpu" in data
    assert "percent" in data["cpu"]
    assert isinstance(data["cpu"]["percent"], (int, float))
    assert 0 <= data["cpu"]["percent"] <= 100
    assert "cores" in data["cpu"]
    assert isinstance(data["cpu"]["cores"], int)
    
    # Check RAM structure
    assert "ram" in data
    assert "used_gb" in data["ram"]
    assert "total_gb" in data["ram"]
    assert "percent" in data["ram"]
    assert isinstance(data["ram"]["used_gb"], (int, float))
    assert isinstance(data["ram"]["total_gb"], (int, float))
    assert 0 <= data["ram"]["percent"] <= 100
    
    # Check GPU structure
    assert "gpu" in data
    assert "available" in data["gpu"]
    assert isinstance(data["gpu"]["available"], bool)
    assert "percent" in data["gpu"]
    assert isinstance(data["gpu"]["percent"], (int, float))
