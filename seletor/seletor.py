from flask import Flask, jsonify, request
from seletor_controller import SeletorController

app = Flask(__name__)
seletor_controller = SeletorController()

@app.route('/seletor/register', methods=['POST'])
def register_validator():
    return seletor_controller.register_validator(request.json)

@app.route('/seletor/trans', methods=['POST'])
def handle_transaction():
    return seletor_controller.handle_transaction(request.json)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
