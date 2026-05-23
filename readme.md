# Sistema de Biblioteca Digital

Sistema web para gerenciamento de biblioteca digital, focado em controle de acervo, empréstimos e relatórios, com controle de acesso baseado em funções (RBAC).

## Funcionalidades
- Autenticação e cadastro de leitores.
- Gerenciamento de administradores e bibliotecários.
- Catálogo de livros com busca.
- Fluxo de empréstimo (solicitação, aprovação e devolução).
- Relatórios e métricas do sistema.

## Tecnologias
- Python 3.12+
- Flask 3.0.0
- SQLite
- Pytest (Testes automatizados)

## Como executar

### Pré-requisitos
- Python instalado.
- Virtualenv recomendado.

### Instalação
1. Clone o repositório.
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r biblioteca_digital/requirements.txt
   ```
4. Configure as variáveis de ambiente (copie o `.env.example` para `.env` se disponível).

### Execução
```bash
cd biblioteca_digital
python run.py
```

### Testes
Para rodar a suíte completa de testes:
```bash
cd biblioteca_digital
PYTHONPATH=. python -m pytest tests/
```

## Arquitetura
O sistema segue um padrão MVC simplificado utilizando Blueprints do Flask para modularização dos controladores e modelos de dados para abstração do banco de dados SQLite.
