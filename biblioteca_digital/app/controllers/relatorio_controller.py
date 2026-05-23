from flask import Blueprint, render_template, session, flash, redirect, url_for
from app.database import conectar_db

relatorio_bp = Blueprint('relatorio', __name__)

def tem_permissao(papeis_permitidos):
    return 'user_papel' in session and session['user_papel'] in papeis_permitidos

@relatorio_bp.route('/relatorios')
def relatorios():
    if not tem_permissao(['ADMIN_INICIAL', 'ADMIN', 'BIBLIOTECARIO']):
        flash('Acesso negado')
        return redirect(url_for('auth.index'))
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Contagem de empréstimos por status
    cursor.execute('SELECT status, COUNT(*) as total FROM emprestimos GROUP BY status')
    status_contagem = cursor.fetchall()
    
    # Top livros mais emprestados
    cursor.execute('''
        SELECT l.titulo, COUNT(e.id) as total 
        FROM livros l 
        JOIN emprestimos e ON l.id = e.livro_id 
        GROUP BY l.id 
        ORDER BY total DESC 
        LIMIT 5
    ''')
    top_livros = cursor.fetchall()
    
    # Distribuição por categoria
    cursor.execute('SELECT categoria, COUNT(*) as total FROM livros GROUP BY categoria')
    categorias_dist = cursor.fetchall()
    
    conn.close()
    
    dados = {
        'status_contagem': status_contagem,
        'top_livros': top_livros,
        'categorias_dist': categorias_dist
    }
    
    return render_template('relatorios.html', dados=dados)
