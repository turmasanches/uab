from flask import Blueprint, render_template, request, session, abort, redirect, url_for
from app.models.livro_model import LivroModel
from app.utils import verificar_permissao
from functools import lru_cache

livro_bp = Blueprint('livro', __name__)

@lru_cache(maxsize=32)
def _buscar_livros_cached(filtros_tuple):
    filtros = dict(filtros_tuple)
    return LivroModel.buscar_todos(filtros)

@livro_bp.route('/catalogo')
def listar_catalogo():
    titulo = request.args.get('titulo')
    autor = request.args.get('autor')
    categoria = request.args.get('categoria')
    livro_id = request.args.get('id')
    
    filtros = {
        'titulo': titulo,
        'autor': autor,
        'categoria': categoria,
        'id': livro_id
    }
    
    # Create a tuple of items sorted by key to be hashable and stable
    filtros_tuple = tuple(sorted(filtros.items()))
    
    livros = _buscar_livros_cached(filtros_tuple)
    return render_template('catalogo.html', livros=livros)

@livro_bp.route('/livro/cadastrar', methods=['GET', 'POST'])
def cadastrar_livro():
    verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL'])
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        categoria = request.form.get('categoria')
        
        livro = LivroModel(titulo, autor, categoria)
        livro.salvar()
        _buscar_livros_cached.cache_clear()
        return redirect(url_for('livro.listar_catalogo'))
    return render_template('livro/cadastrar_livro.html')
