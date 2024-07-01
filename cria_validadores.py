import requests

# =============================== REGISTRO DE VALIDADORES =============================== 
response = requests.post('http://localhost:5001/seletor/register/aaaaaaaaaa/10')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/b/69')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/c/666')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/d/6969')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/e/9669')
print(response.text)

