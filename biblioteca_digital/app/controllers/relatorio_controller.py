from flask import Blueprint, render_template, session, abort
from app.database import conectar_db
from app.utils import verificar_permissao

relatorio_bp = Blueprint('relatorio', __name__)

@relatorio_bp.route('/relatorios')
def relatorios():
    verificar_permissao(['ADMIN', 'BIBLIOTECARIO', 'ADMIN_INICIAL'])
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    # 1. Contagem por status
    cursor.execute('SELECT status, COUNT(*) FROM emprestimos GROUP BY status')
    status_contagem = cursor.fetchall()
    
    # 2. Top Livros (mais solicitados)
    cursor.execute('''
        SELECT l.titulo, COUNT(e.id) as total
        FROM livros l
        LEFT JOIN emprestimos e ON l.id = e.livro_id
        GROUP BY l.id
        ORDER BY total DESC
        LIMIT 5
    ''')
    top_livros = cursor.fetchall()
    
    # 3. Distribuição por categorias
    cursor.execute('''
        SELECT categoria, COUNT(*) as total
        FROM livros
        GROUP BY categoria
    ''')
    categorias_dist = cursor.fetchall()
    
    conn.close()
    
    dados = {
        'status_contagem': status_contagem,
        'top_livros': top_livros,
        'categorias_dist': categorias_dist
    }
    
    return render_template('relatorios.html', dados=dados)
