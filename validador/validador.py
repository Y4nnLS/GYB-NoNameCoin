from flask import Flask, jsonify, request
from validador_controller import ValidadorController

app = Flask(__name__)
validador_controller = ValidadorController()

@app.route('/validador', methods=['POST'])
def validate_transaction():
    return validador_controller.validate_transaction(request.json)

@app.route('/validador/register', methods=['POST'])
def register_validator():
    return validador_controller.register_validator(request.json)

if __name__ == '__main__':
    app.run(port=5002, debug=True)
