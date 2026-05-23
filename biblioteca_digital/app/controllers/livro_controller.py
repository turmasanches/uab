from flask import Blueprint, render_template, request, session, abort, redirect, url_for
from app.models.livro_model import LivroModel

livro_bp = Blueprint('livro', __name__)

def verificar_permissao(papeis_permitidos):
    papel_usuario = session.get('papel')
    if not papel_usuario or papel_usuario not in papeis_permitidos:
        abort(403)

@livro_bp.route('/catalogo')
def listar_catalogo():
    titulo = request.args.get('titulo')
    autor = request.args.get('autor')
    categoria = request.args.get('categoria')
    livro_id = request.args.get('id') # Added for internal lookups
    
    filtros = {
        'titulo': titulo,
        'autor': autor,
        'categoria': categoria,
        'id': livro_id
    }
    
    livros = LivroModel.buscar_todos(filtros)
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
        return redirect(url_for('livro.listar_catalogo'))
    return render_template('livro/cadastrar_livro.html')
