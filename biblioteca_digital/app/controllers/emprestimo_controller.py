from flask import Blueprint, request, session, abort, redirect, url_for, flash, render_template
from app.models.emprestimo_model import EmprestimoModel
from app.models.livro_model import LivroModel

emprestimo_bp = Blueprint('emprestimo', __name__)

def verificar_permissao(papeis_permitidos):
    papel_usuario = session.get('papel')
    if not papel_usuario or papel_usuario not in papeis_permitidos:
        abort(403)

@emprestimo_bp.route('/emprestimo/gerenciar', methods=['GET'])
def gerenciar():
    verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL'])
    emprestimos = EmprestimoModel.buscar_todos()
    return render_template('emprestimo/gerenciar.html', emprestimos=emprestimos)

@emprestimo_bp.route('/emprestimo/solicitar', methods=['POST'])
def solicitar():
    verificar_permissao(['LEITOR'])
    livro_id = request.form.get('livro_id')
    livro = LivroModel.buscar_por_id(livro_id)
    
    if not livro or livro.status != 'DISPONIVEL':
        abort(400, description="Livro não disponível para empréstimo.")
        
    usuario_id = session.get('usuario_id')
    
    emprestimo = EmprestimoModel(livro_id, usuario_id)
    emprestimo.registrar_emprestimo()
    livro.atualizar_status('REQUISITADO')
    return redirect(url_for('livro.listar_catalogo'))

@emprestimo_bp.route('/emprestimo/aprovar', methods=['POST'])
def aprovar():
    verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL'])
    emprestimo_id = request.form.get('emprestimo_id')
    emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
    
    if emprestimo and emprestimo.status == 'SOLICITADO':
        emprestimo.aprovar_emprestimo()
        
        livros = LivroModel.buscar_todos({'id': emprestimo.livro_id})
        if livros:
            livros[0].atualizar_status('EMPRESTADO')
        
    return redirect(url_for('auth.index'))

@emprestimo_bp.route('/emprestimo/devolver', methods=['POST'])
def devolver():
    verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL'])
    emprestimo_id = request.form.get('emprestimo_id')
    emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
    
    if emprestimo:
        emprestimo.finalizar_emprestimo()
        livros = LivroModel.buscar_todos({'id': emprestimo.livro_id})
        if livros:
            livros[0].atualizar_status('DISPONIVEL')
        
    return redirect(url_for('auth.index'))
