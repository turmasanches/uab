import pytest
from app import criar_app
from app.models.usuario_model import UsuarioModel
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

def test_create_admin_by_initial_admin(client, app):
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['papel'] = 'ADMIN_INICIAL'
    
    response = client.post('/admin/cadastrar-admin', data={
        'nome': 'New Admin',
        'email': 'admin@test.com',
        'senha': 'password'
    })
    
    assert response.status_code == 201
    user = UsuarioModel.buscar_por_email('admin@test.com')
    assert user is not None
    assert user.papel == 'ADMIN'

def test_create_admin_restricted(client, app):
    with client.session_transaction() as sess:
        sess['usuario_id'] = 2
        sess['papel'] = 'ADMIN'
    
    response = client.post('/admin/cadastrar-admin', data={
        'nome': 'Another Admin',
        'email': 'admin2@test.com',
        'senha': 'password'
    })
    
    assert response.status_code == 403

def test_create_librarian_by_admin(client, app):
    with client.session_transaction() as sess:
        sess['usuario_id'] = 2
        sess['papel'] = 'ADMIN'
    
    response = client.post('/admin/cadastrar-bibliotecario', data={
        'nome': 'New Librarian',
        'email': 'lib@test.com',
        'senha': 'password'
    })
    
    assert response.status_code == 201
    user = UsuarioModel.buscar_por_email('lib@test.com')
    assert user is not None
    assert user.papel == 'BIBLIOTECARIO'

def test_create_librarian_by_initial_admin(client, app):
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['papel'] = 'ADMIN_INICIAL'
    
    response = client.post('/admin/cadastrar-bibliotecario', data={
        'nome': 'New Librarian 2',
        'email': 'lib2@test.com',
        'senha': 'password'
    })
    
    assert response.status_code == 201
    user = UsuarioModel.buscar_por_email('lib2@test.com')
    assert user is not None
    assert user.papel == 'BIBLIOTECARIO'
