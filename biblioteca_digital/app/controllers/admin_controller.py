from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from app.models.usuario_model import UsuarioModel

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def tem_permissao(papeis_permitidos):
    return 'user_papel' in session and session['user_papel'] in papeis_permitidos

@admin_bp.route('/cadastrar-admin', methods=['GET', 'POST'])
def cadastrar_admin():
    if not tem_permissao(['ADMIN_INICIAL']):
        flash('Acesso negado')
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if UsuarioModel.buscar_por_email(email):
            flash('Email já cadastrado')
        else:
            senha_hash = generate_password_hash(senha)
            novo_admin = UsuarioModel(nome, email, senha_hash, 'ADMIN')
            novo_admin.salvar()
            flash('Administrador cadastrado com sucesso!')
            
    return render_template('admin/cadastrar_usuario.html', papel_alvo='ADMIN')

@admin_bp.route('/cadastrar-bibliotecario', methods=['GET', 'POST'])
def cadastrar_bibliotecario():
    if not tem_permissao(['ADMIN_INICIAL', 'ADMIN']):
        flash('Acesso negado')
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if UsuarioModel.buscar_por_email(email):
            flash('Email já cadastrado')
        else:
            senha_hash = generate_password_hash(senha)
            novo_bib = UsuarioModel(nome, email, senha_hash, 'BIBLIOTECARIO')
            novo_bib.salvar()
            flash('Bibliotecário cadastrado com sucesso!')
            
    return render_template('admin/cadastrar_usuario.html', papel_alvo='BIBLIOTECARIO')
