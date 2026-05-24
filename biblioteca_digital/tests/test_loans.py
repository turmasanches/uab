import pytest
from app import criar_app
from app.models.usuario_model import UsuarioModel
from app.models.livro_model import LivroModel
from app.models.emprestimo_model import EmprestimoModel
from werkzeug.security import generate_password_hash
import os
import tempfile

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    os.environ['DATABASE_PATH'] = db_path
    app = criar_app()
    app.config.update({"TESTING": True})
    yield app
    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_loan_lifecycle(client, app):
    with app.app_context():
        # Setup: Reader, Librarian, and a Book with REAL hashes
        reader = UsuarioModel("Reader", "reader@test.com", generate_password_hash("password"), "LEITOR")
        reader.salvar()
        librarian = UsuarioModel("Librarian", "lib@test.com", generate_password_hash("password"), "BIBLIOTECARIO")
        librarian.salvar()
        book = LivroModel("Python Basics", "Guido", "Programming")
        book.salvar()
    
    # 1. Reader requests loan
    with client.session_transaction() as sess:
        sess['usuario_id'] = reader.id
        sess['papel'] = 'LEITOR'
        sess['nome'] = 'Reader'

    response = client.post('/emprestimo/solicitar', data={'livro_id': book.id}, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify loan status
    loan = EmprestimoModel.buscar_por_id(1)
    assert loan is not None
    assert loan.status == 'SOLICITADO'
    # Verify book status
    updated_book = LivroModel.buscar_todos({'id': book.id})[0]
    assert updated_book.status == 'REQUISITADO'
    
    # 2. Librarian approves loan
    with client.session_transaction() as sess:
        sess['usuario_id'] = librarian.id
        sess['papel'] = 'BIBLIOTECARIO'
        sess['nome'] = 'Librarian'

    response = client.post('/emprestimo/aprovar', data={'emprestimo_id': 1}, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify status changes
    loan = EmprestimoModel.buscar_por_id(1)
    assert loan.status == 'ATIVO'
    updated_book = LivroModel.buscar_todos({'id': book.id})[0]
    assert updated_book.status == 'EMPRESTADO'
    
    # 3. Librarian returns book
    response = client.post('/emprestimo/devolver', data={'emprestimo_id': 1}, follow_redirects=True)
    assert response.status_code == 200
    
    loan = EmprestimoModel.buscar_por_id(1)
    assert loan.status == 'DEVOLVIDO'
    updated_book = LivroModel.buscar_todos({'id': book.id})[0]
    assert updated_book.status == 'DISPONIVEL'

def test_prevent_loan_of_borrowed_book(client, app):
    with app.app_context():
        reader1 = UsuarioModel("Reader1", "r1@test.com", generate_password_hash("p"), "LEITOR")
        reader1.salvar()
        book = LivroModel("Book", "Author", "Cat", status='EMPRESTADO')
        book.salvar()
    
    with client.session_transaction() as sess:
        sess['usuario_id'] = reader1.id
        sess['papel'] = 'LEITOR'

    response = client.post('/emprestimo/solicitar', data={'livro_id': book.id})
    assert response.status_code == 400

def test_loan_access_unauthorized(client, app):
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['papel'] = 'ADMIN' # Admin cannot solicit a loan, only LEITOR
    
    response = client.post('/emprestimo/solicitar', data={'livro_id': 1})
    assert response.status_code == 403

def test_admin_approves_loan(client, app):
    with app.app_context():
        reader = UsuarioModel("Reader", "reader@test.com", generate_password_hash("password"), "LEITOR")
        reader.salvar()
        admin = UsuarioModel("Admin", "admin@test.com", generate_password_hash("password"), "ADMIN")
        admin.salvar()
        book = LivroModel("Python Basics", "Guido", "Programming")
        book.salvar()
        loan = EmprestimoModel(book.id, reader.id)
        loan.registrar_emprestimo()

    with client.session_transaction() as sess:
        sess['usuario_id'] = admin.id
        sess['papel'] = 'ADMIN'
        sess['nome'] = 'Admin'

    response = client.post('/emprestimo/aprovar', data={'emprestimo_id': 1}, follow_redirects=True)
    assert response.status_code == 200

    updated_loan = EmprestimoModel.buscar_por_id(1)
    assert updated_loan.status == 'ATIVO'

def test_loan_filters(client, app):
    with app.app_context():
        lib = UsuarioModel("Lib", "l@t.com", generate_password_hash("p"), "BIBLIOTECARIO")
        lib.salvar()
        reader = UsuarioModel("Reader", "r@t.com", generate_password_hash("p"), "LEITOR")
        reader.salvar()
        b1 = LivroModel("B1", "A1", "C1")
        b1.salvar()
        b2 = LivroModel("B2", "A2", "C2")
        b2.salvar()
        
        # Loan 1: SOLICITADO
        l1 = EmprestimoModel(b1.id, reader.id, status='SOLICITADO')
        l1.registrar_emprestimo()
        # Loan 2: ATIVO
        l2 = EmprestimoModel(b2.id, reader.id, status='ATIVO')
        l2.registrar_emprestimo()

    with client.session_transaction() as sess:
        sess['usuario_id'] = lib.id
        sess['papel'] = 'BIBLIOTECARIO'
        sess['nome'] = 'Lib'
    
    # Check filter: SOLICITADO
    resp = client.get('/emprestimo/gerenciar?status=SOLICITADO')
    assert b"bg-info" in resp.data
    assert b"bg-primary" not in resp.data
    
    # Check filter: ATIVO
    resp = client.get('/emprestimo/gerenciar?status=ATIVO')
    assert b"bg-primary" in resp.data
    assert b"bg-info" not in resp.data

def test_devolutions_search(client, app):
    with app.app_context():
        lib = UsuarioModel("Lib", "l@t.com", generate_password_hash("p"), "BIBLIOTECARIO")
        lib.salvar()
        reader = UsuarioModel("Reader", "r@t.com", generate_password_hash("p"), "LEITOR")
        reader.salvar()
        b1 = LivroModel("B1", "A1", "C1")
        b1.salvar()
        
        # Loan: DEVOLVIDO with date
        l1 = EmprestimoModel(b1.id, reader.id, status='DEVOLVIDO')
        l1.registrar_emprestimo()
        l1.finalizar_emprestimo() # This sets data_devolucao
        
        dev_date = l1.data_devolucao.split(' ')[0]

    with client.session_transaction() as sess:
        sess['usuario_id'] = lib.id
        sess['papel'] = 'BIBLIOTECARIO'
        sess['nome'] = 'Lib'
    
    # Search by date
    resp = client.get(f'/emprestimo/buscar_devolvidos?data={dev_date}')
    assert b"DEVOLVIDO" in resp.data
    
    # Search by invalid date
    resp = client.get('/emprestimo/buscar_devolvidos?data=2020-01-01')
    assert b"DEVOLVIDO" not in resp.data

def test_devolutions_search_access(client, app):
    # LEITOR cannot access
    with app.app_context():
        reader = UsuarioModel("Reader", "r@t.com", generate_password_hash("p"), "LEITOR")
        reader.salvar()
    
    with client.session_transaction() as sess:
        sess['usuario_id'] = reader.id
        sess['papel'] = 'LEITOR'
    
    resp = client.get('/emprestimo/buscar_devolvidos')
    assert resp.status_code == 403

def test_excluir_solicitacao(client, app):
    with app.app_context():
        lib = UsuarioModel("Lib", "l@t.com", generate_password_hash("p"), "BIBLIOTECARIO")
        lib.salvar()
        reader = UsuarioModel("Reader", "r@t.com", generate_password_hash("p"), "LEITOR")
        reader.salvar()
        b1 = LivroModel("B1", "A1", "C1", status='REQUISITADO')
        b1.salvar()
        
        # Loan: SOLICITADO
        l1 = EmprestimoModel(b1.id, reader.id, status='SOLICITADO')
        l1.registrar_emprestimo()
        
    with client.session_transaction() as sess:
        sess['usuario_id'] = lib.id
        sess['papel'] = 'BIBLIOTECARIO'
        sess['nome'] = 'Lib'
    
    # Exclude loan
    resp = client.post('/emprestimo/excluir', data={'emprestimo_id': 1}, follow_redirects=True)
    assert resp.status_code == 200
    
    # Verify loan deleted
    with app.app_context():
        assert EmprestimoModel.buscar_por_id(1) is None
        
        # Verify book available
        updated_book = LivroModel.buscar_todos({'id': b1.id})[0]
        assert updated_book.status == 'DISPONIVEL'
