from flask import Blueprint, request, session, abort, redirect, url_for, render_template
from app.models.usuario_model import UsuarioModel
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

def verificar_permissao(papeis_permitidos):
    papel_usuario = session.get('papel')
    if not papel_usuario or papel_usuario not in papeis_permitidos:
        abort(403)

@admin_bp.route('/admin/cadastrar-admin', methods=['GET', 'POST'])
def cadastrar_admin():
    verificar_permissao(['ADMIN_INICIAL'])
    if request.method == 'GET':
        return render_template('admin/cadastrar_usuario.html', papel_alvo='Administrador')
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    hash_senha = generate_password_hash(senha)
    user = UsuarioModel(nome, email, hash_senha, 'ADMIN')
    user.salvar()
    return redirect(url_for('auth.index'))

@admin_bp.route('/admin/cadastrar-bibliotecario', methods=['GET', 'POST'])
def cadastrar_bibliotecario():
    verificar_permissao(['ADMIN_INICIAL', 'ADMIN'])
    if request.method == 'GET':
        return render_template('admin/cadastrar_usuario.html', papel_alvo='Bibliotecário')
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    hash_senha = generate_password_hash(senha)
    user = UsuarioModel(nome, email, hash_senha, 'BIBLIOTECARIO')
    user.salvar()
    return redirect(url_for('auth.index'))
