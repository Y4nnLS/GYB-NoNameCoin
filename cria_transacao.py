import requests
import json

# =============================== SIMULAR TRANSAÇÃO =============================== 
print("Iniciando criação de transação...")
response = requests.post('http://localhost:5000/transacoes/1/2/10')
print(response.text)
