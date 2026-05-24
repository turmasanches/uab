# Plano de Testes - Sistema de Biblioteca Digital

Este documento detalha o Plano de Testes para o Sistema de Biblioteca Digital, seguindo a abordagem **TDD First (Test-Driven Development)**. O objetivo é garantir a integridade das funcionalidades críticas, a segurança do controle de acesso (RBAC) e a estabilidade do sistema contra regressões.

## 1. Estratégia de Testes

A estratégia foca em testes automatizados utilizando o framework `pytest`. Adotaremos uma pirâmide de testes composta majoritariamente por testes de integração e testes de unidade para a lógica de negócio nos modelos.

### Abordagem TDD First
1. **Red**: Escrever um teste que falha para uma funcionalidade ainda não implementada ou um cenário crítico.
2. **Green**: Implementar o código mínimo necessário para fazer o teste passar.
3. **Refactor**: Melhorar o código mantendo os testes passando.

---

## 2. Ambiente de Testes

### Dependências Necessárias
Para a execução dos testes, as seguintes bibliotecas devem ser adicionadas ao `requirements.txt`:
- `pytest`: Framework de testes.
- `pytest-flask`: Extensão para integração com Flask.
- `coverage`: Para medição de cobertura de código.

### Configuração do Banco de Dados de Teste
Os testes utilizarão um banco de dados SQLite em memória (`:memory:`) ou um arquivo temporário exclusivo para testes, garantindo isolamento e rapidez.

---

## 3. Plano de Testes por Funcionalidade

### 3.1. Autenticação e Cadastro (`auth_controller.py`)

| ID | Cenário | Prioridade | Descrição |
|:---|:---|:---|:---|
| TEST-AUTH-01 | Login com sucesso | Crítica | Validar se um usuário cadastrado consegue iniciar sessão. |
| TEST-AUTH-02 | Login com senha inválida | Crítica | Garantir que o acesso seja negado para credenciais incorretas. |
| TEST-AUTH-03 | Cadastro de Leitor | Alta | Validar se o autocadastro cria corretamente um usuário com papel 'LEITOR'. |
| TEST-AUTH-04 | Logout | Média | Verificar se a sessão é devidamente destruída ao deslogar. |
| TEST-AUTH-05 | Exibição de Usuário no Menu | Média | Validar se o nome do usuário logado aparece na barra de menu em páginas protegidas. |

### 3.2. Gerenciamento de Usuários (RBAC) (`admin_controller.py`)

| ID | Cenário | Prioridade | Descrição |
|:---|:---|:---|:---|
| TEST-RBAC-01 | Cadastro de Admin por Admin Inicial | Crítica | Validar se apenas o 'ADMIN_INICIAL' pode criar outros administradores. |
| TEST-RBAC-02 | Restrição de acesso Admin | Alta | Garantir que um 'LEITOR' não consiga acessar rotas de cadastro de administradores. |
| TEST-RBAC-03 | Cadastro de Bibliotecário | Alta | Validar se 'ADMIN' e 'ADMIN_INICIAL' conseguem criar bibliotecários. |

### 3.3. Catálogo de Livros (`livro_controller.py`)

| ID | Cenário | Prioridade | Descrição |
|:---|:---|:---|:---|
| TEST-BOOK-01 | Busca no Catálogo | Alta | Validar se os filtros de busca (título, autor, categoria) retornam os resultados corretos. |
| TEST-BOOK-02 | Verificação de Dados de Teste | Alta | Validar se 30 livros foram cadastrados automaticamente na inicialização. |
| TEST-BOOK-03 | Cadastro de Livro (Permissão) | Crítica | Validar se apenas 'BIBLIOTECARIO' ou 'ADMIN' podem cadastrar livros. |
| TEST-BOOK-04 | Opção de Cadastro e Gestão de Empréstimos no Menu | Alta | Garantir que a opção 'Cadastrar Livro' e 'Gerenciar Empréstimos' só apareça para usuários com papel ADMIN ou BIBLIOTECARIO. |
| TEST-BOOK-05 | Cadastro com dados incompletos | Média | Garantir que o sistema valide campos obrigatórios no cadastro. |

### 3.4. Fluxo de Empréstimo (Cenários Críticos) (`emprestimo_controller.py`)

| ID | Cenário | Prioridade | Descrição |
|:---|:---|:---|:---|
| TEST-LOAN-01 | Solicitação de Empréstimo | Crítica | Validar se um 'LEITOR' pode solicitar um livro disponível. |
| TEST-LOAN-02 | Mudança de status para REQUISITADO | Crítica | Validar se o status do livro muda para 'REQUISITADO' logo após a solicitação do leitor. |
| TEST-LOAN-03 | Livro Indisponível | Crítica | Impedir a solicitação de um livro que não esteja com status 'DISPONIVEL' (validação estrita do valor retornado pelo banco). |
| TEST-LOAN-04 | Aprovação de Empréstimo (BIBLIOTECARIO) | Alta | Validar se o status do livro muda para 'EMPRESTADO' após aprovação do bibliotecário. |
| TEST-LOAN-05 | Aprovação de Empréstimo (ADMIN) | Alta | Validar se o status do livro muda para 'EMPRESTADO' após aprovação do administrador. |
| TEST-LOAN-06 | Devolução de Livro | Alta | Garantir que o livro volte a ficar 'DISPONIVEL' após a devolução. |
| TEST-LOAN-07 | Filtro 'Aguardando Aprovação' | Alta | Validar se o filtro exibe apenas empréstimos 'SOLICITADO'. |
| TEST-LOAN-08 | Filtro 'Emprestados' | Alta | Validar se o filtro exibe apenas empréstimos 'ATIVO'. |
| TEST-LOAN-09 | Busca Devoluções por Data | Alta | Validar busca de empréstimos 'DEVOLVIDO' por data. |
| TEST-LOAN-10 | Permissão Busca Devoluções | Crítica | Garantir que apenas ADMIN/BIBLIOTECARIO podem buscar devoluções. |
| TEST-LOAN-11 | Exclusão de Solicitação | Alta | Validar se um bibliotecário/admin pode excluir uma solicitação pendente e o livro volta a ficar disponível. |

### 3.5. Relatórios (`relatorio_controller.py`)

| ID | Cenário | Prioridade | Descrição |
|:---|:---|:---|:---|
| TEST-REP-01 | Acesso a Relatórios | Alta | Validar se usuários sem permissão (LEITOR) são bloqueados. |
| TEST-REP-02 | Integridade dos Dados | Média | Verificar se a contagem de empréstimos reflete a realidade do banco de dados. |

### 3.6. Segurança e Consistência de Sessão

| ID | Cenário | Prioridade | Descrição |
|:---|:---|:---|:---|
| TEST-SESS-01 | Consistência de Chaves de Sessão | Alta | Validar se as chaves da sessão (`usuario_id`, `nome`, `papel`) estão sendo utilizadas de forma consistente em todo o sistema, evitando chaves alternativas (ex: `user_papel`). |

---

## 4. Automação e Validação

### Execução dos Testes
Para rodar a suíte completa de testes:
```bash
pytest
```

### Validação de Regressão e Cobertura
Para garantir que novas alterações não quebrem funcionalidades existentes e verificar a abrangência dos testes:
```bash
coverage run -m pytest
coverage report -m
```

### Mocks
Serão utilizados mocks (através de `unittest.mock`) para simular:
- Envio de e-mails (se implementado futuramente).
- Integrações com APIs externas de busca de livros (ex: Google Books API).
- Relógio do sistema para validação de datas de devolução.
