import pytest
from flask import json

from loadbalancer import loadbalancer


@pytest.fixture
def client():
    with loadbalancer.test_client() as client:
        yield client


def test_host_routing_mango(client):
    result = client.get("/", headers={"Host": "www.mango.com"})
    data = json.loads(result.data.decode())
    assert "This is the mango application." in data["message"]
    assert data["server"] in ["http://localhost:8082/", "http://localhost:8081/"]


def test_host_routing_apple(client):
    result = client.get("/", headers={"Host": "www.apple.com"})
    data = json.loads(result.data.decode())
    assert "This is the apple application." in data["message"]
    assert data["server"] in ["http://localhost:9082/", "http://localhost:9081/"]


def test_host_routing_orange(client):
    result = client.get("/", headers={"Host": "www.orange.com"})
    assert b"No backend servers available." in result.data


def test_host_routing_notfound(client):
    result = client.get("/", headers={"Host": "www.notmango.com"})
    assert b"Not Found" in result.data
    assert 404 == result.status_code


def test_path_routing_mango(client):
    result = client.get("/mango")
    data = json.loads(result.data.decode())
    assert "This is the mango application." in data["message"]
    assert data["server"] in ["http://localhost:8082/", "http://localhost:8081/"]


def test_path_routing_apple(client):
    result = client.get("/apple")
    data = json.loads(result.data.decode())
    assert "This is the apple application." in data["message"]
    assert data["server"] in ["http://localhost:9082/", "http://localhost:9081/"]


def test_path_routing_orange(client):
    result = client.get("/orange")
    assert b"No backend servers available." in result.data


def test_path_routing_notfound(client):
    result = client.get("/notmango")
    assert b"Not Found" in result.data
    assert 404 == result.status_code
