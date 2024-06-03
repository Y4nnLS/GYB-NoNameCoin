from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# Simulação de chaves únicas e contas
unique_keys = {}

# Dados do banco simulados para transações e contas
accounts = {
    "user1": {"balance": 1000, "last_transaction_time": None, "transaction_count": 0},
    "user2": {"balance": 500, "last_transaction_time": None, "transaction_count": 0},
}

transactions = [
    {
        "id": 1,
        "sender": "user1",
        "receiver": "user2",
        "amount": 100,
        "fee": 1,
        "timestamp": "2024-06-01T12:00:00",
        "status": 0,
        "unique_key": None
    }
]

@app.route('/validador', methods=['POST'])
def validador():
    data = request.json
    transaction_id = data['transaction_id']
    validator_id = data['validator_id']
    unique_key = data['unique_key']
    
    # Verificar chave única
    if unique_key != unique_keys.get(validator_id):
        return jsonify({"status": 2, "message": "Chave única inválida"}), 400

    # Encontrar a transação
    transaction = next((t for t in transactions if t["id"] == transaction_id), None)
    if not transaction:
        return jsonify({"status": 2, "message": "Transação não encontrada"}), 400

    sender = transaction['sender']
    amount = transaction['amount']
    fee = transaction['fee']
    timestamp = datetime.datetime.fromisoformat(transaction['timestamp'])
    current_time = datetime.datetime.now()

    # Verificar saldo suficiente
    if accounts[sender]['balance'] < amount + fee:
        return jsonify({"status": 2, "message": "Saldo insuficiente"}), 400

    # Verificar se o horário da transação é válido
    if timestamp > current_time or (accounts[sender]['last_transaction_time'] and timestamp <= accounts[sender]['last_transaction_time']):
        return jsonify({"status": 2, "message": "Horário da transação inválido"}), 400

    # Verificar o limite de transações por minuto
    if accounts[sender]['last_transaction_time'] and (current_time - accounts[sender]['last_transaction_time']).seconds < 60:
        accounts[sender]['transaction_count'] += 1
        if accounts[sender]['transaction_count'] > 100:
            return jsonify({"status": 2, "message": "Limite de transações por minuto excedido"}), 400
    else:
        accounts[sender]['transaction_count'] = 1

    accounts[sender]['balance'] -= amount + fee
    accounts[sender]['last_transaction_time'] = current_time

    accounts[transaction['receiver']]['balance'] += amount

    return jsonify({"status": 1, "message": "Transação validada com sucesso"}), 200

@app.route('/validador/register_key', methods=['POST'])
def register_key():
    data = request.json
    validator_id = data['validator_id']
    unique_key = data['unique_key']
    unique_keys[validator_id] = unique_key
    return jsonify({"status": 1, "message": "Chave registrada com sucesso"}), 200

@app.route('/validador/register_transaction', methods=['POST'])
def register_transaction():
    data = request.json
    transactions.append(data)
    return jsonify({"status": 1, "message": "Transação registrada com sucesso"}), 200

@app.route('/validador/keys', methods=['GET'])
def get_keys():
    return jsonify(unique_keys)

@app.route('/validador/accounts', methods=['GET'])
def get_accounts():
    return jsonify(accounts)

@app.route('/validador/transactions', methods=['GET'])
def get_transactions():
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
