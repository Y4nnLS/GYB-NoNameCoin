import requests

# Criando clientes
response = requests.post('http://localhost:5000/cliente/pinto/1234/500')
print(response.text)
response = requests.post('http://localhost:5000/cliente/cu/1234/500')
print(response.text)
response = requests.post('http://localhost:5000/cliente/fds/1234/500')
print(response.text)

# Editando clientes
response = requests.post('http://localhost:5000/cliente/1/250')
print(response.text)
response = requests.post('http://localhost:5000/cliente/2/300')
print(response.text)
response = requests.delete('http://localhost:5000/cliente/3')
print(response.text)

# Criando seletores
response = requests.post('http://localhost:5000/seletor/seletor1/123.123')
print(response.text)
response = requests.post('http://localhost:5000/seletor/seletor2/122.122')
print(response.text)

# Editando seletores
response = requests.post('http://localhost:5000/seletor/1/seletorB/111111')
print(response.text)
response = requests.post('http://localhost:5000/seletor/2/seletorA/222222')
print(response.text)
response = requests.delete('http://localhost:5000/seletor/2')

print(response.text)
response = requests.get('http://localhost:5000/cliente/3')

print(response.text)