import pytest
from app import criar_app
from app.models.livro_model import LivroModel
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

def test_catalog_search(client, app):
    with app.app_context():
        l1 = LivroModel("Python for Beginners", "John Doe", "Programming")
        l1.salvar()
        l2 = LivroModel("Learning Java", "Jane Smith", "Programming")
        l2.salvar()
        l3 = LivroModel("Cooking 101", "Chef Bob", "Hobbies")
        l3.salvar()

    # Search by title
    response = client.get('/catalogo?titulo=Python')
    assert response.status_code == 200
    assert b"Python for Beginners" in response.data
    assert b"Learning Java" not in response.data

    # Search by author
    response = client.get('/catalogo?autor=Jane')
    assert response.status_code == 200
    assert b"Learning Java" in response.data
    assert b"Python for Beginners" not in response.data

    # Search by category
    response = client.get('/catalogo?categoria=Hobbies')
    assert response.status_code == 200
    assert b"Cooking 101" in response.data
    assert b"Learning Java" not in response.data

def test_create_book_authorized(client, app):
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['papel'] = 'BIBLIOTECARIO'
    
    response = client.post('/livro/cadastrar', data={
        'titulo': 'New Book',
        'autor': 'Author Name',
        'categoria': 'Test'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"New Book" in response.data
    
    books = LivroModel.buscar_todos({'titulo': 'New Book'})
    assert len(books) == 1

def test_get_create_book_page(client, app):
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['papel'] = 'BIBLIOTECARIO'
    
    response = client.get('/livro/cadastrar')
    assert response.status_code == 200
    assert b"Cadastrar Novo Livro" in response.data

def test_create_book_unauthorized(client, app):
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['papel'] = 'LEITOR'
    
    response = client.post('/livro/cadastrar', data={
        'titulo': 'Unauthorized Book',
        'autor': 'Author',
        'categoria': 'Test'
    })
    
    assert response.status_code == 403

def test_register_book_option_visibility(client, app):
    # Case 1: Librarian should see the option
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['papel'] = 'BIBLIOTECARIO'
    
    response = client.get('/catalogo')
    assert b"Cadastrar Livro" in response.data

    # Case 2: Reader should NOT see the option
    with client.session_transaction() as sess:
        sess['usuario_id'] = 2
        sess['papel'] = 'LEITOR'
    
    response = client.get('/catalogo')
    assert b"Cadastrar Livro" not in response.data
