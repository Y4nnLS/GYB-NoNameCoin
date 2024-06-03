from flask import Flask, request, jsonify
import datetime
import requests

app = Flask(__name__)

# Simulação de contas e transações
accounts = {
    "user1": {"balance": 1000, "last_transaction_time": None, "transaction_count": 0},
    "user2": {"balance": 500, "last_transaction_time": None, "transaction_count": 0},
}

transactions = []

@app.route('/')
def home():
    return "Bem-vindo ao Banco da NoNameCoin!"

@app.route('/trans', methods=['POST'])
def create_transaction():
    data = request.json
    sender = data['sender']
    receiver = data['receiver']
    amount = data['amount']
    fee = data.get('fee', 1)
    timestamp = datetime.datetime.now().isoformat()

    if sender not in accounts or receiver not in accounts:
        return jsonify({"status": 2, "message": "Conta inválida"}), 400

    transaction = {
        "id": len(transactions) + 1,
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "fee": fee,
        "timestamp": timestamp,
        "status": 0,
        "unique_key": None
    }
    transactions.append(transaction)
    
    # Registrar a transação no validador
    register_transaction(transaction)

    # Selecionar validadores automaticamente
    select_validators_response = select_validators(transaction["id"])
    
    if select_validators_response["status"] == 1:
        selected_validators = select_validators_response["selected_validators"]
        validation_results = validate_transaction_with_validators(transaction["id"], selected_validators)
        return jsonify({"status": 1, "transaction": transaction, "validation_results": validation_results}), 201
    else:
        return jsonify({"status": 2, "message": "Validadores insuficientes, transação em espera"}), 400

def select_validators(transaction_id):
    url = 'http://127.0.0.1:5001/seletor/select'
    payload = {
        "transaction_id": transaction_id
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def validate_transaction_with_validators(transaction_id, validators):
    results = []
    for validator_id in validators:
        result = validate_transaction(transaction_id, validator_id)
        results.append(result)
    return results

def validate_transaction(transaction_id, validator_id):
    url = 'http://127.0.0.1:5002/validador'
    payload = {
        "transaction_id": transaction_id,
        "validator_id": validator_id,
        "unique_key": f"key{validator_id[-1]}"  # Assuming unique_key is "key1", "key2", "key3", etc.
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def register_transaction(transaction):
    url = 'http://127.0.0.1:5002/validador/register_transaction'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=transaction, headers=headers)
    return response.json()

@app.route('/accounts', methods=['GET'])
def get_accounts():
    return jsonify(accounts)

@app.route('/transactions', methods=['GET'])
def get_transactions():
    return jsonify(transactions)

@app.route('/hora', methods=['GET'])
def get_time():
    return jsonify({"current_time": datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
