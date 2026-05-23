from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.usuario_model import UsuarioModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = UsuarioModel.buscar_por_email(email)
        if usuario and check_password_hash(usuario.senha_hash, senha):
            session['user_id'] = usuario.id
            session['user_nome'] = usuario.nome
            session['user_papel'] = usuario.papel
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos')
            
    return render_template('login.html')

@auth_bp.route('/cadastrar-leitor', methods=['GET', 'POST'])
def cadastrar_leitor():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if UsuarioModel.buscar_por_email(email):
            flash('Email já cadastrado')
        else:
            senha_hash = generate_password_hash(senha)
            novo_usuario = UsuarioModel(nome, email, senha_hash, 'LEITOR')
            novo_usuario.salvar()
            flash('Cadastro realizado com sucesso! Faça login.')
            return redirect(url_for('auth.login'))
            
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html')
