import requests

# =============================== REGISTRO DE VALIDADORES =============================== 
response = requests.post('http://localhost:5001/seletor/register/validador1/69.0')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/validador2/69.0')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/validador3/69.0')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/validador4/666.0')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/validador5/6969.0')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/validador6/9669.0')
print(response.text)

