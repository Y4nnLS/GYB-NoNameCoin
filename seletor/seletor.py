from flask import Flask, request, jsonify
import random
import datetime
import requests
from collections import defaultdict

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
    
    if stake < 50:
        return jsonify({"status": 2, "message": "Saldo mínimo insuficiente"}), 400
    
    unique_key = f"key{len(validators) + 1}"
    validators[validator_id] = {
        "stake": stake,
        "unique_key": unique_key,
        "flags": 0,
        "in_hold": False,
        "hold_count": 0,
        "last_selected": None,
        "coherent_transactions": 0,
        "consecutive_selections": 0,
        "expulsions": 0,
        "total_selections": 0
    }

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
        pending_transactions.append((transaction_id, datetime.datetime.now()))
        return jsonify({"status": 2, "message": "Validadores insuficientes, transação em espera"}), 400
    
    available_validators = {k: v for k, v in validators.items() if not v['in_hold']}
    
    if len(available_validators) < 3:
        pending_transactions.append((transaction_id, datetime.datetime.now()))
        return jsonify({"status": 2, "message": "Validadores insuficientes disponíveis, transação em espera"}), 400

    selected_validators = select_based_on_stake(available_validators)

    for validator in selected_validators:
        validators[validator]['last_selected'] = datetime.datetime.now()
        validators[validator]['consecutive_selections'] += 1
        validators[validator]['total_selections'] += 1
        if validators[validator]['consecutive_selections'] >= 5:
            validators[validator]['in_hold'] = True
            validators[validator]['hold_count'] = 5

    transaction_log.append({
        "transaction_id": transaction_id,
        "selected_validators": selected_validators,
        "timestamp": datetime.datetime.now().isoformat()
    })

    update_validators_after_selection(selected_validators)
    
    return jsonify({"status": 1, "selected_validators": selected_validators})

def select_based_on_stake(validators):
    total_stake = sum(v['stake'] for v in validators.values())
    validator_weights = []
    for validator_id, validator in validators.items():
        weight = validator['stake']
        if validator['flags'] == 1:
            weight *= 0.5
        elif validator['flags'] == 2:
            weight *= 0.25
        
        max_weight = total_stake * 0.2
        weight = min(weight, max_weight)
        validator_weights.extend([validator_id] * int(weight))

    selected_validators = []
    while len(selected_validators) < 3:
        selected = random.choices(validator_weights, k=1)[0]
        if selected not in selected_validators:
            selected_validators.append(selected)

    return selected_validators

def update_validators_after_selection(selected_validators):
    for validator in selected_validators:
        validators[validator]['coherent_transactions'] += 1
        if validators[validator]['coherent_transactions'] >= 10000:
            validators[validator]['coherent_transactions'] -= 10000
            if validators[validator]['flags'] > 0:
                validators[validator]['flags'] -= 1
        
        if validators[validator]['flags'] >= 2:
            validators[validator]['expulsions'] += 1
            if validators[validator]['expulsions'] > 2:
                del validators[validator]
            else:
                validators[validator]['stake'] *= 2
        
        if validators[validator]['in_hold']:
            validators[validator]['hold_count'] -= 1
            if validators[validator]['hold_count'] == 0:
                validators[validator]['in_hold'] = False
                validators[validator]['consecutive_selections'] = 0

@app.route('/seletor/consensus', methods=['POST'])
def get_consensus():
    data = request.json
    transaction_id = data['transaction_id']
    votes = data['votes']  # Expects a dictionary with validator_id as key and vote as value
    
    if len(votes) < 3:
        return jsonify({"status": 2, "message": "Votos insuficientes para consenso"}), 400
    
    vote_counts = defaultdict(int)
    for vote in votes.values():
        vote_counts[vote] += 1
    
    consensus_vote = max(vote_counts, key=vote_counts.get)
    if vote_counts[consensus_vote] > len(votes) / 2:
        status = "Aprovada" if consensus_vote == "Aprovada" else "Não Aprovada"
        return jsonify({"status": 1, "consensus": status}), 200
    else:
        return jsonify({"status": 2, "message": "Consenso não alcançado"}), 400

@app.route('/seletor/validators', methods=['GET'])
def get_validators():
    return jsonify(validators)

@app.route('/seletor/pending_transactions', methods=['GET'])
def get_pending_transactions():
    now = datetime.datetime.now()
    pending_transactions[:] = [t for t in pending_transactions if (now - t[1]).seconds < 60]
    return jsonify([t[0] for t in pending_transactions])

@app.route('/seletor/log', methods=['GET'])
def get_log():
    return jsonify(transaction_log)

@app.route('/seletor/return_validator', methods=['POST'])
def return_validator():
    data = request.json
    validator_id = data['validator_id']
    stake = data['stake']
    
    if validator_id not in validators:
        return jsonify({"status": 2, "message": "Validador não encontrado"}), 400

    if validators[validator_id]['expulsions'] >= 2:
        return jsonify({"status": 2, "message": "Retorno não permitido, validador foi expulso mais de duas vezes"}), 400
    
    if stake < validators[validator_id]['stake'] * 2:
        return jsonify({"status": 2, "message": "Saldo insuficiente para retorno"}), 400
    
    validators[validator_id]['stake'] = stake
    validators[validator_id]['expulsions'] = 0
    
    return jsonify({"status": 1, "message": "Validador retornou à rede"}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5001)
