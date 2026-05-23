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
