import pytest
from flask import session
from app import criar_app
from app.database import inicializar_db
from app.models.usuario_model import UsuarioModel
from werkzeug.security import generate_password_hash
import os
import tempfile

@pytest.fixture
def app():
    # Create a temporary file for the database
    db_fd, db_path = tempfile.mkstemp()
    os.environ['DATABASE_PATH'] = db_path
    
    app = criar_app()
    app.config.update({
        "TESTING": True,
    })
    
    with app.app_context():
        # Tables are created by criar_app -> inicializar_db
        pass
    
    yield app
    
    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_reader_registration(client):
    response = client.post('/cadastrar-leitor', data={
        'nome': 'New Reader',
        'email': 'reader@example.com',
        'senha': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    user = UsuarioModel.buscar_por_email('reader@example.com')
    assert user is not None
    assert user.papel == 'LEITOR'

def test_login_success(client, app):
    with app.app_context():
        user = UsuarioModel("Login User", "login@example.com", generate_password_hash("pass"), "LEITOR")
        user.salvar()
    
    response = client.post('/login', data={
        'email': 'login@example.com',
        'senha': 'pass'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert sess['usuario_id'] is not None
        assert sess['papel'] == 'LEITOR'

def test_login_failure(client, app):
    with app.app_context():
        user = UsuarioModel("Login User", "wrong@example.com", generate_password_hash("pass"), "LEITOR")
        user.salvar()
    
    response = client.post('/login', data={
        'email': 'wrong@example.com',
        'senha': 'wrong_pass'
    })
    
    assert response.status_code == 302 # Redirect back to login
    with client.session_transaction() as sess:
        assert 'usuario_id' not in sess

def test_rbac_admin_only(client, app):
    # Register a simple reader
    client.post('/cadastrar-leitor', data={
        'nome': 'Reader', 'email': 'r@e.com', 'senha': 'p'
    })
    client.post('/login', data={'email': 'r@e.com', 'senha': 'p'})
    
    # Try to access admin route
    response = client.post('/admin/cadastrar-admin', data={
        'nome': 'New Admin', 'email': 'a@e.com', 'senha': 'p'
    })
    assert response.status_code == 403
