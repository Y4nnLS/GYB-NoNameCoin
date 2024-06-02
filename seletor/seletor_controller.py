from flask import jsonify
import requests
import random

VALIDATOR_SERVICE_URL = "http://127.0.0.1:5002/validador"

class SeletorController:
    """
    Classe que gerencia os validadores e processa as transações, selecionando validadores para obter consenso.

    Attributes:
        validators (list): Lista de validadores registrados.
    """

    def __init__(self):
        """
        Inicializa uma nova instância de SeletorController.
        """
        self.validators = []

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
            'flag': 0
        }
        self.validators.append(validator)
        return jsonify(validator), 201

    def handle_transaction(self, data):
        """
        Lida com uma transação selecionando validadores e obtendo consenso.

        Args:
            data (dict): Dicionário contendo as informações da transação (transaction_id e amount).

        Returns:
            Response: Resposta JSON com o status do consenso e os resultados das validações, ou erro caso não haja validadores suficientes.
        """
        # Selecionar validadores para a transação
        if len(self.validators) < 3:
            return jsonify({'error': 'Not enough validators registered'}), 400
        
        selected_validators = random.sample(self.validators, 3)
        results = []

        for validator in selected_validators:
            response = requests.post(VALIDATOR_SERVICE_URL, json={
                'transaction_id': data['transaction_id'],
                'amount': data['amount'],
                'validator_id': validator['id']
            })
            results.append(response.json())

        # Determinar o consenso
        success_count = sum(1 for result in results if result['status'] == 'success')
        failure_count = len(results) - success_count

        if success_count > failure_count:
            consensus_status = 'success'
        else:
            consensus_status = 'failed'

        return jsonify({
            'transaction_id': data['transaction_id'],
            'consensus_status': consensus_status,
            'results': results
        }), 200
