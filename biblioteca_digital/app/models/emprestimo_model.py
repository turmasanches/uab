from app.database import conectar_db
from datetime import datetime

class EmprestimoModel:
    def __init__(self, livro_id, usuario_id, data_solicitacao=None, data_devolucao=None, status='SOLICITADO', id=None):
        self.id = id
        self.livro_id = livro_id
        self.usuario_id = usuario_id
        self.data_solicitacao = data_solicitacao
        self.data_devolucao = data_devolucao
        self.status = status

    def registrar_emprestimo(self):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emprestimos (livro_id, usuario_id, status)
            VALUES (?, ?, ?)
        ''', (self.livro_id, self.usuario_id, self.status))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_por_id(id):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM emprestimos WHERE id = ?', (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return EmprestimoModel(row['livro_id'], row['usuario_id'], row['data_solicitacao'], row['data_devolucao'], row['status'], row['id'])
        return None

    def finalizar_emprestimo(self):
        self.status = 'DEVOLVIDO'
        self.data_devolucao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE emprestimos 
            SET status = ?, data_devolucao = ?
            WHERE id = ?
        ''', (self.status, self.data_devolucao, self.id))
        conn.commit()
        conn.close()

    def atualizar_status(self, novo_status):
        self.status = novo_status
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE emprestimos SET status = ? WHERE id = ?', (self.status, self.id))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.*, l.titulo as livro_titulo, u.nome as usuario_nome
            FROM emprestimos e
            JOIN livros l ON e.livro_id = l.id
            JOIN usuarios u ON e.usuario_id = u.id
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        resultado = []
        for row in rows:
            emp = EmprestimoModel(row['livro_id'], row['usuario_id'], row['data_solicitacao'], row['data_devolucao'], row['status'], row['id'])
            emp.livro_titulo = row['livro_titulo']
            emp.usuario_nome = row['usuario_nome']
            resultado.append(emp)
        return resultado
