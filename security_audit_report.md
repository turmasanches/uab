# Security Audit Report - Sistema de Biblioteca Digital

## Resumo Executivo

Este relatório apresenta os resultados de uma inspeção de segurança realizada no projeto "Sistema de Biblioteca Digital". O sistema apresenta vulnerabilidades críticas que expõem dados de usuários e permitem acesso indevido.

### Contagem de Achados por Severidade

| Severidade | Quantidade |
| :--- | :--- |
| Crítica | 2 |
| Alta | 2 |
| Média | 1 |
| Baixa | 1 |

### 5 Ações Mais Urgentes

1.  **Corrigir `SECRET_KEY`:** Alterar a `SECRET_KEY` para um valor forte e único, definido via variável de ambiente, e remover o `hardcoding` no `app/__init__.py`.
2.  **Desativar `DEBUG_MODE`:** Garantir que `DEBUG_MODE` seja `False` em ambiente de produção.
3.  **Implementar Validação de Entrada:** Adicionar validação rigorosa para todos os campos de formulários em todos os controladores.
4.  **Implementar Controle de Acesso:** Adicionar decoradores de autorização (ex: `@login_required`, `@role_required`) em todas as rotas protegidas.
5.  **Revisar Configurações de Sessão e Cookies:** Definir atributos seguros para cookies de sessão (HttpOnly, Secure, SameSite).

---

## Detalhamento das Vulnerabilidades

### 1. Uso de Segredos Hardcoded
- **Localização:** `app/__init__.py`, linha 9.
- **Descrição:** A `SECRET_KEY` do Flask está definida como `'test_secret'`. Isso compromete a segurança de todas as sessões assinadas.
- **Impacto Potencial:** Atacantes podem falsificar cookies de sessão e escalar privilégios.
- **Severidade:** Crítica
- **Recomendação:** Utilizar variáveis de ambiente para gerenciar segredos.
- **Ref:** CWE-798: Use of Hard-coded Credentials.

### 2. DEBUG_MODE ativado por padrão
- **Localização:** `config.py`, linha 11.
- **Descrição:** `DEBUG_MODE` pode ser ativado facilmente. Se habilitado em produção, permite execução remota de código via debugger do Werkzeug.
- **Impacto Potencial:** Execução Remota de Código (RCE).
- **Severidade:** Crítica
- **Recomendação:** Garantir que em produção o modo debug esteja desativado (`False`).
- **Ref:** CWE-489: Leftover Debug Code.

### 3. Falta de Controle de Acesso (Broken Access Control)
- **Localização:** `app/controllers/*.py` (rotas protegidas).
- **Descrição:** Várias rotas não verificam se o usuário está logado ou possui o papel necessário.
- **Impacto Potencial:** Acesso não autorizado a funcionalidades administrativas ou de outros usuários.
- **Severidade:** Alta
- **Ref:** OWASP A01:2021-Broken Access Control.

### 4. Falta de Validação de Entrada
- **Localização:** `app/controllers/auth_controller.py`, `cadastrar_leitor`.
- **Descrição:** Não há validação dos dados enviados pelo usuário (nome, email, senha).
- **Impacto Potencial:** Injeção de dados maliciosos, cadastro de usuários com dados inválidos.
- **Severidade:** Alta
- **Ref:** OWASP A05:2021-Injection.

### 5. Configuração insegura de sessões
- **Localização:** Não identificado explicitamente.
- **Descrição:** Falta de configuração de atributos seguros para cookies de sessão (HttpOnly, Secure, SameSite).
- **Impacto Potencial:** Roubo de sessão via XSS ou interceptação de rede.
- **Severidade:** Média
- **Ref:** OWASP A02:2021-Security Misconfiguration.

### 6. Senhas padrão
- **Localização:** `config.py`, linha 10.
- **Descrição:** `PROPRIETARIO_PASSWORD` possui um valor padrão fraco (`senha_segura`).
- **Impacto Potencial:** Acesso fácil a contas administrativas se não alterada.
- **Severidade:** Baixa
- **Ref:** CWE-521: Weak Password Requirements.
