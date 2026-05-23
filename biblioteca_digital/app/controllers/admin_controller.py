from flask import Blueprint, request, session, abort, redirect, url_for
from app.models.usuario_model import UsuarioModel
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

def verificar_permissao(papeis_permitidos):
    papel_usuario = session.get('papel')
    if not papel_usuario or papel_usuario not in papeis_permitidos:
        abort(403)

@admin_bp.route('/admin/cadastrar-admin', methods=['POST'])
def cadastrar_admin():
    verificar_permissao(['ADMIN_INICIAL'])
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    hash_senha = generate_password_hash(senha)
    user = UsuarioModel(nome, email, hash_senha, 'ADMIN')
    user.salvar()
    return "Admin cadastrado", 201

@admin_bp.route('/admin/cadastrar-bibliotecario', methods=['POST'])
def cadastrar_bibliotecario():
    verificar_permissao(['ADMIN_INICIAL', 'ADMIN'])
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    hash_senha = generate_password_hash(senha)
    user = UsuarioModel(nome, email, hash_senha, 'BIBLIOTECARIO')
    user.salvar()
    return "Bibliotecario cadastrado", 201
