import requests

response = requests.get('http://localhost:5001/')
print(response.text)

response = requests.post('http://localhost:5001/seletor/register/pinto/69')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/cu/666')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/bosta/6969')
print(response.text)
response = requests.post('http://localhost:5001/seletor/register/mijo/9669')
print(response.text)
