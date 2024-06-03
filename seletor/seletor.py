from flask import Flask, request, jsonify
import random
import datetime
import requests

app = Flask(__name__)

validators = {}
pending_transactions = []
transaction_log = []

@app.route('/seletor/register', methods=['POST'])
def register_validator():
    data = request.json
    validator_id = data['validator_id']
    stake = data['stake']
    
    if validator_id in validators:
        return jsonify({"status": 2, "message": "Validador já registrado"}), 400
    
    unique_key = f"key{len(validators) + 1}"
    validators[validator_id] = {
        "stake": stake,
        "unique_key": unique_key,
        "flags": 0,
        "in_hold": False,
        "hold_count": 0,
        "last_selected": None,
        "coherent_transactions": 0
    }

    # Register the unique key automatically with the validator service
    register_validator_key(validator_id, unique_key)
    
    return jsonify({"status": 1, "unique_key": unique_key}), 201

def register_validator_key(validator_id, unique_key):
    url = 'http://127.0.0.1:5002/validador/register_key'
    payload = {
        "validator_id": validator_id,
        "unique_key": unique_key
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@app.route('/seletor/select', methods=['POST'])
def select_validators():
    data = request.json
    transaction_id = data['transaction_id']
    
    if len(validators) < 3:
        pending_transactions.append(transaction_id)
        return jsonify({"status": 2, "message": "Validadores insuficientes, transação em espera"}), 400
    
    # Seleção dos validadores
    available_validators = {k: v for k, v in validators.items() if not v['in_hold']}
    selected_validators = random.sample(list(available_validators.keys()), 3)
    
    for validator in selected_validators:
        validators[validator]['last_selected'] = datetime.datetime.now()
    
    transaction_log.append({
        "transaction_id": transaction_id,
        "selected_validators": selected_validators,
        "timestamp": datetime.datetime.now().isoformat()
    })
    
    return jsonify({"status": 1, "selected_validators": selected_validators})

@app.route('/seletor/validators', methods=['GET'])
def get_validators():
    return jsonify(validators)

@app.route('/seletor/pending_transactions', methods=['GET'])
def get_pending_transactions():
    return jsonify(pending_transactions)

@app.route('/seletor/log', methods=['GET'])
def get_log():
    return jsonify(transaction_log)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
