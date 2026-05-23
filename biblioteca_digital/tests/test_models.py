import pytest
import os
import tempfile
from config import Config

# Setup a clean test environment for models
db_fd, db_path = tempfile.mkstemp()
os.environ['DATABASE_PATH'] = db_path

from app.database import inicializar_db, conectar_db
from app.models.usuario_model import UsuarioModel
from app.models.livro_model import LivroModel
from app.models.emprestimo_model import EmprestimoModel

@pytest.fixture(autouse=True)
def setup_db():
    inicializar_db()
    yield
    # Clean up tables between tests
    conn = conectar_db()
    conn.execute("DELETE FROM usuarios")
    conn.execute("DELETE FROM livros")
    conn.execute("DELETE FROM emprestimos")
    conn.commit()
    conn.close()

def test_usuario_model_salvar_e_buscar():
    user = UsuarioModel("Test User", "test@example.com", "hash", "LEITOR")
    user.salvar()
    
    fetched_user = UsuarioModel.buscar_por_email("test@example.com")
    assert fetched_user is not None
    assert fetched_user.nome == "Test User"
    assert fetched_user.papel == "LEITOR"

def test_livro_model_salvar_e_buscar():
    book = LivroModel("Test Title", "Test Author", "Test Category")
    book.salvar()
    
    books = LivroModel.buscar_todos({"titulo": "Test Title"})
    assert len(books) == 1
    assert books[0].titulo == "Test Title"
    assert books[0].status == "DISPONIVEL"

def test_livro_model_atualizar_status():
    book = LivroModel("Test Title", "Test Author", "Test Category")
    book.salvar()
    # Ensure we use the ID assigned during salvar
    book.atualizar_status("EMPRESTADO")
    
    books = LivroModel.buscar_todos({"id": book.id})
    assert len(books) == 1
    assert books[0].status == "EMPRESTADO"

def test_emprestimo_model_fluxo():
    user = UsuarioModel("Reader", "reader@example.com", "hash", "LEITOR")
    user.salvar()
    book = LivroModel("Book", "Author", "Cat")
    book.salvar()
    
    loan = EmprestimoModel(book.id, user.id)
    loan.registrar_emprestimo()
    assert loan.id is not None
    assert loan.status == "SOLICITADO"
    
    loan.finalizar_emprestimo()
    assert loan.status == "DEVOLVIDO"
    assert loan.data_devolucao is not None
    
    fetched_loan = EmprestimoModel.buscar_por_id(loan.id)
    assert fetched_loan.status == "DEVOLVIDO"
