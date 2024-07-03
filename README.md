<h1 align='center'>
    <p>GYB - NoNameCoin</p>
</h1>

## 🙋‍♂️ Equipe de desenvolvedores
<table align='center'>
  <tr>
    <td align="center">
        <img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/101208372?v=4" width="100px;" alt=""/><br /><sub><b><a href="https://github.com/Y4nnLS">Yann Lucas</a></b></sub></a><br />🤓☝</a></td>
    <td align="center">
        <img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/60533993?v=4" width="100px;" alt=""/><br /><sub><b><a href="https://github.com/Ypsiloon">Felipe Pinheiro</a></b></sub></a><br />🤠✊</td>
  </table>

# Projeto de Sistema Distribuído para Validação de Transações

Este projeto implementa um sistema distribuído para validação de transações utilizando uma arquitetura baseada em microserviços com Flask e SQLAlchemy. Ele inclui módulos para seleção de validadores, validação de transações e gerenciamento de logs.

## Estrutura do Projeto

O projeto é dividido em três principais componentes:

1. **Seletor**: Responsável por selecionar validadores para transações e coordenar o processo de validação.
2. **Validador**: Responsável por validar transações individuais com base em regras específicas.
3. **Banco**: Responsável por armazenar transações e gerenciar contas de usuários.

## Funcionalidades Implementadas

### Seletor

- **Seleção de Validadores**: Utiliza um algoritmo dinâmico para selecionar validadores com base no peso do stake e flags de alerta.
- **Gerenciamento de Validadores**: Permite inserção e remoção de validadores, mantendo registro de todas as eleições.

### Validador

- **Validação de Transações**: Implementa regras rigorosas para validar transações, incluindo verificação de saldo, horário da transação e controle de transações por minuto.
- **Registro e Verificação de Chave Única**: Cada validador deve registrar e utilizar uma chave única para garantir a autenticidade da transação.

### Banco

- **Armazenamento Seguro**: Utiliza SQLite para armazenar transações e logs de eventos.
- **Sincronização de Tempo**: Mantém sincronia com o servidor para garantir que todas as transações sejam temporalmente consistentes.

## Regras de Validação Implementadas

1. **Regras de Validação**:
   - Verificação de saldo suficiente do remetente.
   - Validade do horário da transação.
   - Controle de transações por minuto.
   - Verificação da chave única recebida pelo seletor.

2. **Regras de Seleção de Validadores**:
   - Seleção de no mínimo três validadores.
   - Consenso baseado em mais de 50% de aprovação.
   - Ajuste dinâmico do peso do validador com base em flags de alerta.
   - Controle de expulsões e retornos de validadores.

## Arquitetura e Tecnologias

- **Flask**: Framework web utilizado para construir os microserviços.
- **SQLAlchemy**: Biblioteca de ORM para interação com o banco de dados SQLite.
- **Requests**: Biblioteca para realizar requisições HTTP entre os serviços.

## Execução do Projeto

Para executar o projeto localmente:

1. Clone este repositório.
3. Execute cada componente (`seletor.py`, `validador.py`, `banco.py`) em terminais separados usando Python.

```bash
python seletor.py
python validador.py
python banco.py
```

Certifique-se de configurar os endpoints corretamente nos arquivos conforme necessário para a execução dos serviços.

## Considerações Finais

Este projeto atende aos requisitos especificados para um sistema distribuído de validação de transações, utilizando práticas de programação distribuída e web services. Para mais detalhes sobre a implementação de cada componente, consulte o código-fonte fornecido.


