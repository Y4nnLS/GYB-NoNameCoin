import pytest
from validador import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_register_validator(client):
    rv = client.post('/validador/register', json={
        "name": "Validator1",
        "stake": 100
    })
    json_data = rv.get_json()
    assert rv.status_code == 201
    assert json_data['name'] == "Validator1"

def test_validate_transaction(client):
    rv = client.post('/validador', json={
        "transaction_id": 1,
        "amount": 50,
        "validator_id": 1
    })
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data['status'] == "success"
