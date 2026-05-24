from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from app.models.usuario_model import UsuarioModel
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user = UsuarioModel.buscar_por_email(email)
        
        if user and check_password_hash(user.senha_hash, senha):
            session['usuario_id'] = user.id
            session['nome'] = user.nome
            session['papel'] = user.papel
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('auth.index'))
        
        flash('Email ou senha inválidos.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/cadastrar-leitor', methods=['GET', 'POST'])
def cadastrar_leitor():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        hash_senha = generate_password_hash(senha)
        user = UsuarioModel(nome, email, hash_senha, 'LEITOR')
        user.salvar()
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/')
def index():
    return render_template('index.html')
