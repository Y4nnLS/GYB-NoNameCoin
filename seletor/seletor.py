# Outras importações
from flask import Flask, request, jsonify
import random
import requests
import os
import secrets
import string
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dataclasses import dataclass
from datetime import datetime, timedelta

app = Flask(__name__)

# Caminho para o banco de dados
db_path = os.path.join(os.getcwd(), 'seletor/banco')
db_file = 'seletor.db'
if not os.path.exists(db_path):
    os.makedirs(db_path)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_path, db_file)}'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@dataclass
class Validador(db.Model):
    id: int
    name: str
    stake: float
    flags: int
    in_hold: bool
    hold_count: int
    last_selected: int
    coherent_transactions: int
    consecutive_selections: int
    expulsions: int
    total_selections: int
    unique_key: str  # Alterado para tipo str
    initial_stake: float
    expelled_count: int

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    stake = db.Column(db.Float, nullable=False)
    flags = db.Column(db.Integer, nullable=False, default=0)
    in_hold = db.Column(db.Boolean, nullable=False, default=False)
    hold_count = db.Column(db.Integer, nullable=False, default=0)
    last_selected = db.Column(db.Integer, nullable=False, default=0)
    coherent_transactions = db.Column(db.Integer, nullable=False, default=0)
    consecutive_selections = db.Column(db.Integer, nullable=False, default=0)
    expulsions = db.Column(db.Integer, nullable=False, default=0)
    total_selections = db.Column(db.Integer, nullable=False, default=0)
    unique_key = db.Column(db.String(16), nullable=False)  # Chave única como string
    initial_stake = db.Column(db.Float, nullable=False, default=0)
    expelled_count = db.Column(db.Integer, nullable=False, default=0)

def log_event(event, details):
    log = ElectionLog(event=event, details=details)
    db.session.add(log)
    db.session.commit()

@dataclass
class ElectionLog(db.Model):
    id: int
    timestamp: datetime
    event: str
    details: str

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=False)


def generate_unique_key():
    alphabet = string.ascii_letters + string.digits
    unique_key = ''.join(secrets.choice(alphabet) for i in range(16))  # 16 caracteres de comprimento
    return unique_key


def get_last_transaction_and_count(sender):
    current_time = datetime.now()
    one_minute_ago = current_time - timedelta(minutes=1)
    last_transaction = None
    transactions_last_minute_count = 0

    try:
        # Faz a requisição GET para o endpoint /transacoes
        response = requests.get('http://localhost:5000/transacoes')  # Ajuste o endereço conforme necessário

        if response.status_code == 200:
            # Obtém as transações do JSON retornado pela API
            transacoes = response.json()

            # Encontra a última transação do sender
            for transacao in transacoes:
                if transacao.get('sender') == sender:
                    last_transaction = transacao
                    break

            # Conta as transações do sender nos últimos minutos
            transactions_last_minute_count = sum(1 for t in transacoes if t.get('sender') == sender and datetime.strptime(t.get('timestamp'), '%Y-%m-%d %H:%M:%S') >= one_minute_ago)

    except requests.exceptions.RequestException as e:
        print(f'Erro ao fazer requisição para /transacoes: {e}')

    return last_transaction, transactions_last_minute_count


@app.route("/")
def index():
    return jsonify(['API sem interface do banco!'])

@app.route('/seletor/register/<string:name>/<float:stake>', methods=['POST'])
def register_validator(name, stake):
    existing_validator = Validador.query.filter_by(name=name).first()
    
    if existing_validator:
        required_stake = existing_validator.initial_stake * (2 ** existing_validator.expelled_count)
        if existing_validator.expelled_count > 0 and stake < required_stake:
            return jsonify({"status": 2, "message": f"Saldo insuficiente. É necessário pelo menos {required_stake} para retornar à rede."}), 400
        existing_validator.stake = stake
        existing_validator.in_hold = False
        db.session.commit()
    else:
        if stake < 50.0:
            return jsonify({"status": 2, "message": "Saldo mínimo insuficiente"}), 400
        
        if request.method == 'POST' and name != '':
            unique_key = generate_unique_key()
            new_validator = Validador(
                name=name, stake=stake, flags=0, in_hold=False, hold_count=0,
                last_selected=0, coherent_transactions=0, consecutive_selections=0,
                expulsions=0, total_selections=0, unique_key=unique_key,
                initial_stake=stake, expelled_count=0
            )
            db.session.add(new_validator)
            db.session.commit()

            response = requests.post(f'http://localhost:5002/validador/register_key', json={"validator_id": new_validator.id, "unique_key": unique_key})
            if response.status_code == 200:
                return jsonify({"status": 1, "message": "Validador registrado com sucesso"}), 201
            else:
                return jsonify({"status": 2, "message": "Erro ao registrar validador"}), 400
    return jsonify({"status": 1, "message": "Validador registrado com sucesso."})


@app.route('/seletor/select', methods=['POST'])
def select_validators():
    data = request.json
    log_event("START_ELECTION", f"Iniciar processo de eleição para transação {data['transaction_id']}")

    last_transaction, transactions_last_minute_count = get_last_transaction_and_count(data['sender'])

    transaction_details = {
        'id':  data['transaction_id'],
        'sender': data['sender'],
        'sender_amount': data['sender_amount'],
        'receiver': data['receiver'],
        'receiver_amount': data['receiver_amount'],
        'amount': data['transaction_amount'],
        'fee': data['fee'],
        'timestamp': data['timestamp'],
        'last_transaction': last_transaction,
        'transactions_last_minute_count': transactions_last_minute_count
    }
    # last_transaction, transactions_last_minute_count = get_last_transaction_and_count(data['sender'])

    validadores = Validador.query.filter_by(in_hold=False).all()

    if len(validadores) < 3:
        log_event("ELECTION_ERROR", "Validadores insuficientes, transação em espera")
        return jsonify({"status": 2, "message": "Validadores insuficientes, transação em espera"}), 400

    selected_validators = select_based_on_stake(validadores)
    validation_results = []
    log_event("VALIDATORS_SELECTED", f"Validadores selecionados: {selected_validators}")

    
    server_time = get_server_time()
    if server_time is None:
        return jsonify({"status": 2, "message": "Erro ao obter o horário do servidor"}), 500
    
    # Enviar transação para validadores selecionados
    for validador_id in selected_validators:
        validador = db.session.get(Validador, validador_id)
        try:
            url = f'http://localhost:5002/validador'
            data_transaction = {
                'transaction': transaction_details,
                'validator_id': validador_id,
                'unique_key': validador.unique_key,
                'server_time': server_time.isoformat()
            }
            response = requests.post(url, json=data_transaction)

            if response.status_code == 200:
                validation_results.append(response.json())
            else:
                log_event("VALIDATOR_COMMUNICATION_ERROR", f"Erro ao comunicar com o validador {validador.name}: {response.status_code}")
                print(f"Erro ao comunicar com o validador {validador.name}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            log_event("VALIDATOR_CONNECTION_ERROR", f"Falha ao conectar ao validador {validador.name}: {e}")
            print(f"Falha ao conectar ao validador {validador.name}: {e}")

# a gente pode fazer o processo de eleição, se der poggers a gente atualiza os saldos, se der noggers cancela tudo
    # Contadores para aprovações e reprovações
    approved_count = sum(1 for result in validation_results if result['status'] == 1)
    rejected_count = sum(1 for result in validation_results if result['status'] == 2)

    # Verificando se há consenso
    consensus = 'Aprovada' if approved_count > len(validation_results) / 2 else 'Nao Aprovada' if rejected_count > len(validation_results) / 2 else 'Sem consenso'
    log_event("CONSENSUS_RESULT", f"Consenso: {consensus}")

    for result in validation_results:
        validador_id = result['validator_id']
        validador = db.session.get(Validador, validador_id)
        if (consensus == 'Aprovada' and result['status'] != 1) or (consensus == 'Nao Aprovada' and result['status'] != 2):
            validador.flags += 1
            validador.coherent_transactions = 0
            if validador.flags > 2:
                validador.stake = 0
                validador.in_hold = True
                validador.expelled_count += 1
                log_event("VALIDATOR_EXPULSION", f"Validador {validador.name} expulso da rede.")
            db.session.commit()
        else:
            validador.coherent_transactions += 1
            validador.total_selections += 1
            if validador.coherent_transactions >= 10000:
                validador.flags = max(0, validador.flags - 1)
                validador.coherent_transactions = 0
            db.session.commit()
    print(f"Consenso: {consensus}")

    if consensus == 'Aprovada':
        # Autorizar a transação e realizar a transferência de dinheiro
        sender_id = data['sender']
        receiver_id = data['receiver']
        transaction_amount = data['transaction_amount']
        fee = data['fee']
        verdin = transaction_amount * fee
        transaction_amount -= verdin
        taxa_seletor = verdin/3
        taxa_validadores = (verdin-taxa_seletor)/len(validadores)
        response = requests.post(f'http://localhost:5000/seletor/{data["seletor_id"]}/{data["seletor_nome"]}/{data["seletor_ip"]}/{taxa_seletor:.2f}')
        for validador in selected_validators:
            validador = db.session.get(Validador, validador)
            validador.stake += taxa_validadores
            db.session.commit()
        try:
            # Atualizar saldo do remetente
            sender_response = requests.post(f'http://localhost:5000/cliente/{sender_id}', params={'amount': -(transaction_amount)})
            # Atualizar saldo do destinatário
            receiver_response = requests.post(f'http://localhost:5000/cliente/{receiver_id}', params={'amount': transaction_amount})

            if sender_response.status_code == 200 and receiver_response.status_code == 200:
                log_event("END_ELECTION", f"Fim do processo de eleição para a transação {data['transaction_id']}")
                return jsonify({"status": 1, "message": "Transacao aprovada e valores atualizados", "selected_validators": selected_validators, "validation_results": validation_results})
            else:
                return jsonify({"status": 2, "message": "Erro ao atualizar saldos dos usuarios"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"status": 2, "message": f"Falha ao conectar ao serviço de atualização de saldo: {e}"}), 400
    else:
        return jsonify({"status": 2, "message": "Transacao nao aprovada", "selected_validators": selected_validators, "validation_results": validation_results}), 400

@app.route('/seletor/delete/<int:id>', methods = ['DELETE'])
def ApagarSeletor(id):
    if(request.method == 'DELETE'):
        objeto = db.session.get(Validador, id)
        db.session.delete(objeto)
        db.session.commit()
        data={
            "message": "Validador Deletado com Sucesso"
        }

        return jsonify(data)
    else:
        return jsonify(['Method Not Allowed'])

def select_based_on_stake(validators):
    total_stake = sum(v.stake for v in validators)
    validator_weights = []
    for validator in validators:
        weight = validator.stake
        if validator.total_selections > 10000:
            validator.total_selections = 0
            validator.flags -= 1
        if validator.flags == 1:
            weight *= 0.5
        elif validator.flags == 2:
            weight *= 0.25
        elif validator.flags == 3:
            weight *= 0
            validator.expulsions += 1
            validator.in_hold = True
            db.session.commit()

        max_weight = total_stake * 0.2
        weight = min(weight, max_weight)
        validator_weights.extend([validator.id] * int(weight))

    selected_validators = []
    while len(selected_validators) < 3:
        selected = random.choice(validator_weights)
        if selected not in selected_validators:
            selected_validators.append(selected)

    return selected_validators

@app.route('/seletor/election_logs', methods=['GET'])
def get_election_logs():
    logs = ElectionLog.query.all()
    return jsonify([log.to_dict() for log in logs])

def get_server_time():
    try:
        response = requests.get('http://localhost:5000/hora')  # Ajuste o endereço conforme necessário
        if response.status_code == 200:
            data = response.json()
            # O campo do JSON retornado contém a data em formato string
            server_time_str = data.get('datetime')
            # Converte a string de data para um objeto datetime
            if server_time_str.endswith('Z'):
                server_time_str = server_time_str[:-1]
            current_time = datetime.fromisoformat(server_time_str)
            return current_time
    except requests.exceptions.RequestException as e:
        print(f'Erro ao obter o horário do servidor: {e}')
    except ValueError as e:
        print(f'Erro ao converter o horário do servidor: {e}')
    return None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
