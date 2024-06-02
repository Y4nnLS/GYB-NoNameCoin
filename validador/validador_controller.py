from flask import jsonify
import time

class ValidadorController:
    """
    Classe que gerencia validadores, transações e saldos de remetentes.

    Attributes:
        validations (list): Lista de validações realizadas.
        validators (list): Lista de validadores registrados.
        balances (dict): Dicionário que armazena os saldos dos remetentes.
        transactions (dict): Dicionário que armazena o histórico de transações dos remetentes.
    """

    def __init__(self):
        """
        Inicializa uma nova instância de ValidadorController.
        """
        self.validations = []
        self.validators = []
        self.balances = {}  # Armazenar saldos dos remetentes
        self.transactions = {}  # Armazenar histórico de transações

    def register_validator(self, data):
        """
        Registra um novo validador.

        Args:
            data (dict): Dicionário contendo as informações do validador (name e stake).

        Returns:
            Response: Resposta JSON com os dados do validador registrado e o status HTTP 201.
        """
        validator = {
            'id': len(self.validators) + 1,
            'name': data['name'],
            'stake': data['stake'],
            'flag': 0,
            'unique_key': f"key_{len(self.validators) + 1}"  # Chave única
        }
        self.validators.append(validator)
        return jsonify(validator), 201

    def validate_transaction(self, data):
        """
        Valida uma transação.

        Args:
            data (dict): Dicionário contendo as informações da transação (transaction_id, sender, amount, transaction_time, validator_id e validator_key).

        Returns:
            Response: Resposta JSON com os dados da validação realizada e o status HTTP 200.
        """
        validation = {
            'id': len(self.validations) + 1,
            'transaction_id': data['transaction_id'],
            'status': self.check_validity(data),
            'validator_id': data['validator_id']
        }
        self.validations.append(validation)
        return jsonify(validation), 200

    def check_validity(self, data):
        """
        Verifica a validade de uma transação.

        Args:
            data (dict): Dicionário contendo as informações da transação (sender, amount, transaction_time, validator_id e validator_key).

        Returns:
            str: Status da validação ('success' ou mensagem de erro).
        """
        sender = data['sender']
        amount = data['amount']
        transaction_time = data['transaction_time']
        validator_id = data['validator_id']
        validator_key = data['validator_key']

        # Verificar saldo suficiente
        if sender not in self.balances or self.balances[sender] < amount:
            return 'failed: insufficient funds'

        # Verificar horário da transação
        current_time = time.time()
        if transaction_time > current_time:
            return 'failed: invalid transaction time'
        
        # Verificar limite de transações por minuto
        if sender in self.transactions:
            recent_transactions = [t for t in self.transactions[sender] if current_time - t < 60]
            if len(recent_transactions) >= 100:
                return 'failed: too many transactions'
        
        # Verificar chave única do validador
        validator = next((v for v in self.validators if v['id'] == validator_id), None)
        if validator is None or validator['unique_key'] != validator_key:
            return 'failed: invalid validator key'
        
        # Atualizar saldo e histórico de transações
        self.balances[sender] -= amount
        if sender not in self.transactions:
            self.transactions[sender] = []
        self.transactions[sender].append(transaction_time)

        return 'success'

def add_balance(validador_controller, sender, amount):
    """
    Adiciona saldo ao remetente.

    Args:
        validador_controller (ValidadorController): Instância de ValidadorController.
        sender (str): Identificador do remetente.
        amount (float): Quantia a ser adicionada ao saldo.
    """
    if sender in validador_controller.balances:
        validador_controller.balances[sender] += amount
    else:
        validador_controller.balances[sender] = amount

# Exemplo de uso:
# validador_controller = ValidadorController()
# add_balance(validador_controller, 'user1', 1000)
