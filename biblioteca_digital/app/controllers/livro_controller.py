from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.livro_model import LivroModel

livro_bp = Blueprint('livro', __name__)

def tem_permissao(papeis_permitidos):
    return 'user_papel' in session and session['user_papel'] in papeis_permitidos

@livro_bp.route('/catalogo')
def catalogo():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    filtros = {
        'titulo': request.args.get('titulo'),
        'autor': request.args.get('autor'),
        'categoria': request.args.get('categoria')
    }
    livros = LivroModel.buscar_todos(filtros)
    return render_template('catalogo.html', livros=livros)

@livro_bp.route('/livro/cadastrar', methods=['GET', 'POST'])
def cadastrar_livro():
    if not tem_permissao(['ADMIN_INICIAL', 'ADMIN', 'BIBLIOTECARIO']):
        flash('Acesso negado')
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        categoria = request.form.get('categoria')
        
        novo_livro = LivroModel(titulo, autor, categoria)
        novo_livro.salvar()
        flash('Livro cadastrado com sucesso!')
        return redirect(url_for('livro.catalogo'))
            
    return render_template('livro/cadastrar_livro.html')
