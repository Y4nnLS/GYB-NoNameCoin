from flask import Flask, jsonify, request
from seletor_controller import SeletorController

app = Flask(__name__)
seletor_controller = SeletorController()

@app.route('/seletor/register', methods=['POST'])
def register_validator():
    """
    Rota para registrar um novo validador.

    Recebe uma solicitação POST com dados JSON contendo 'name' e 'stake' do validador.

    Returns:
        Response: Resposta JSON com os dados do validador registrado e o status HTTP 201.
    """
    return seletor_controller.register_validator(request.json)

@app.route('/seletor/trans', methods=['POST'])
def handle_transaction():
    """
    Rota para lidar com uma transação.

    Recebe uma solicitação POST com dados JSON contendo 'transaction_id', 'sender', 'amount', 'transaction_time', 'validator_id' e 'validator_key'.

    Returns:
        Response: Resposta JSON com os dados da transação processada e o status HTTP 200.
    """
    """
    {
        "transaction_id" : ,
        "sender" : ,
        "amount" : 50 ,
        "transaction_time" : ,
        "validator_id" : ,
        "validator_key" : 
    }
    """
    return seletor_controller.handle_transaction(request.json)

if __name__ == '__main__':
    """
    Inicializa e executa o servidor Flask na porta 5001 com o modo debug ativado.
    """
    app.run(port=5001, debug=True)
