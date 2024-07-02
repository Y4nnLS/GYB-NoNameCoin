import requests
import json

# =============================== SIMULAR TRANSAÇÃO =============================== 
print("Iniciando criação de transação...")
response = requests.post('http://localhost:5000/transacoes/1/2/10')
print(response.text)
print(f"Resposta do servidor: {response.status_code}")
print(f"Conteúdo da resposta: {response.json()}")



# response = requests.get('http://localhost:5000/cliente/1')
# print(response.text)
# a = response.json()
# print(a['qtdMoeda'])
# transaction_amount= 10
# sender_id = fee = 1

# from operator import neg
# deduct_amount = ((transaction_amount + fee))
# sender_response = requests.post(f'http://localhost:5000/cliente/{sender_id}', params={'amount': -deduct_amount})

# print(sender_response.text)