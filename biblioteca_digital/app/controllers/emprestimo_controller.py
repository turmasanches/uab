from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.emprestimo_model import EmprestimoModel
from app.models.livro_model import LivroModel

emprestimo_bp = Blueprint('emprestimo', __name__, url_prefix='/emprestimo')

def tem_permissao(papeis_permitidos):
    return 'user_papel' in session and session['user_papel'] in papeis_permitidos

@emprestimo_bp.route('/solicitar/<int:livro_id>', methods=['POST'])
def solicitar(livro_id):
    if not tem_permissao(['LEITOR']):
        flash('Acesso negado. Apenas leitores podem solicitar livros.')
        return redirect(url_for('livro.catalogo'))
    
    livro = LivroModel.buscar_por_id(livro_id)
    if not libro:
        flash('Livro não encontrado.')
        return redirect(url_for('livro.catalogo'))
        
    if libro.status != 'DISPONIVEL':
        flash('Livro não disponível para empréstimo.')
        return redirect(url_for('livro.catalogo'))
    
    novo_emprestimo = EmprestimoModel(livro_id, session['user_id'])
    novo_emprestimo.registrar_emprestimo()
    flash('Solicitação de empréstimo enviada!')
    return redirect(url_for('livro.catalogo'))

@emprestimo_bp.route('/gerenciar')
def gerenciar():
    if not tem_permissao(['ADMIN_INICIAL', 'ADMIN', 'BIBLIOTECARIO']):
        flash('Acesso negado')
        return redirect(url_for('auth.index'))
    
    emprestimos = EmprestimoModel.buscar_todos()
    return render_template('emprestimo/gerenciar.html', emprestimos=emprestimos)

@emprestimo_bp.route('/aprovar/<int:emprestimo_id>', methods=['POST'])
def aprovar(emprestimo_id):
    if not tem_permissao(['ADMIN_INICIAL', 'ADMIN', 'BIBLIOTECARIO']):
        flash('Acesso negado')
        return redirect(url_for('auth.index'))
    
    emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
    if emprestimo and emprestimo.status == 'SOLICITADO':
        livro = LivroModel.buscar_por_id(emprestimo.livro_id)
        if libro and libro.status == 'DISPONIVEL':
            emprestimo.atualizar_status('ATIVO')
            libro.atualizar_status('EMPRESTADO')
            flash('Empréstimo aprovado!')
        else:
            flash('Livro não disponível.')
    else:
        flash('Solicitação inválida.')
        
    return redirect(url_for('emprestimo.gerenciar'))

@emprestimo_bp.route('/devolver/<int:emprestimo_id>', methods=['POST'])
def devolver(emprestimo_id):
    if not tem_permissao(['ADMIN_INICIAL', 'ADMIN', 'BIBLIOTECARIO']):
        flash('Acesso negado')
        return redirect(url_for('auth.index'))
    
    emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
    if emprestimo and emprestimo.status == 'ATIVO':
        livro = LivroModel.buscar_por_id(emprestimo.livro_id)
        emprestimo.finalizar_emprestimo()
        if libro:
            libro.atualizar_status('DISPONIVEL')
        flash('Devolução registrada!')
    else:
        flash('Empréstimo inválido.')
        
    return redirect(url_for('emprestimo.gerenciar'))
