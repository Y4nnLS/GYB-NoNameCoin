from flask import Flask, request
from validador_controller import ValidadorController

app = Flask(__name__)
validador_controller = ValidadorController()

@app.route('/validador/register', methods=['POST'])
def register_validator():
    """
    Rota para registrar um novo validador.

    Recebe uma solicitação POST com dados JSON contendo 'name' e 'stake' do validador.

    Returns:
        Response: Resposta JSON com os dados do validador registrado e o status HTTP 201.
    """
    return validador_controller.register_validator(request.json)

@app.route('/validador', methods=['POST'])
def validate_transaction():
    """
    Rota para validar uma transação.

    Recebe uma solicitação POST com dados JSON contendo 'transaction_id', 'sender', 'amount', 'transaction_time', 'validator_id' e 'validator_key'.

    Returns:
        Response: Resposta JSON com os dados da validação realizada e o status HTTP 200.
    """
    return validador_controller.validate_transaction(request.json)

if __name__ == '__main__':
    """
    Inicializa e executa o servidor Flask na porta 5002 com o modo debug ativado.
    """
    app.run(port=5002, debug=True)
