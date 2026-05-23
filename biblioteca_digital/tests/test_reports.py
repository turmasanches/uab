import pytest
from app import criar_app
from app.models.usuario_model import UsuarioModel
from app.models.livro_model import LivroModel
from app.models.emprestimo_model import EmprestimoModel
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

def test_reports_access_restricted(client, app):
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['papel'] = 'LEITOR'
    
    response = client.get('/relatorios')
    assert response.status_code == 403

def test_reports_data_integrity(client, app):
    with app.app_context():
        # Setup: Some books and loans
        book1 = LivroModel("Book 1", "A", "C1")
        book1.salvar()
        book2 = LivroModel("Book 2", "B", "C2")
        book2.salvar()
        reader = UsuarioModel("R", "r@t.com", "h", "LEITOR")
        reader.salvar()
        
        loan1 = EmprestimoModel(book1.id, reader.id)
        loan1.registrar_emprestimo()
        loan2 = EmprestimoModel(book2.id, reader.id)
        loan2.registrar_emprestimo()
    
    with client.session_transaction() as sess:
        sess['usuario_id'] = 2
        sess['papel'] = 'ADMIN'
    
    response = client.get('/relatorios')
    assert response.status_code == 200
    # Check if the data is in the response (using some identifiers)
    assert b'Book 1' in response.data
    assert b'Book 2' in response.data
