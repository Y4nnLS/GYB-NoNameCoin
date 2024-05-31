from flask import jsonify
import random

class ValidadorController:
    def __init__(self):
        self.validations = []
        self.validators = []

    def register_validator(self, data):
        # Registrar um novo validador
        validator = {
            'id': len(self.validators) + 1,
            'name': data['name'],
            'stake': data['stake'],
            'flag': 0
        }
        self.validators.append(validator)
        return jsonify(validator), 201

    def validate_transaction(self, data):
        # Implementar a lógica de validação da transação
        validation = {
            'id': len(self.validations) + 1,
            'transaction_id': data['transaction_id'],
            'status': self.check_validity(data),
            'validator_id': data['validator_id']
        }
        self.validations.append(validation)
        return jsonify(validation), 200

    def check_validity(self, data):
        # Verificar as regras de validação aqui
        # Ex: Saldo suficiente, horário da transação, limite de transações, etc.
        # Supondo uma verificação simples:
        if data['amount'] <= 0:
            return 'failed'
        # Mais lógica pode ser adicionada aqui para validar a transação conforme as regras
        return 'success'
