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
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO emprestimos (livro_id, usuario_id, status)
                VALUES (?, ?, ?)
            ''', (self.livro_id, self.usuario_id, self.status))
            conn.commit()
            self.id = cursor.lastrowid
        finally:
            conn.close()

    def aprovar_emprestimo(self):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE emprestimos 
                SET status = 'ATIVO' 
                WHERE id = ?
            ''', (self.id,))
            conn.commit()
            self.status = 'ATIVO'
        finally:
            conn.close()

    def finalizar_emprestimo(self):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            self.data_devolucao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE emprestimos 
                SET status = 'DEVOLVIDO', data_devolucao = ? 
                WHERE id = ?
            ''', (self.data_devolucao, self.id))
            conn.commit()
            self.status = 'DEVOLVIDO'
        finally:
            conn.close()

    def excluir_solicitacao(self):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM emprestimos WHERE id = ?', (self.id,))
            conn.commit()
        finally:
            conn.close()
        
    @staticmethod
    def buscar_por_id(id):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM emprestimos WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return EmprestimoModel(row['livro_id'], row['usuario_id'], row['data_solicitacao'], row['data_devolucao'], row['status'], row['id'])
        finally:
            conn.close()
        return None

    @staticmethod
    def buscar_todos(filtros=None):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            query = '''
                SELECT e.*, l.titulo as livro_titulo, u.nome as usuario_nome
                FROM emprestimos e
                JOIN livros l ON e.livro_id = l.id
                JOIN usuarios u ON e.usuario_id = u.id
            '''
            params = []
            if filtros:
                conditions = []
                if 'status' in filtros:
                    conditions.append('e.status = ?')
                    params.append(filtros['status'])
                if 'data_devolucao' in filtros:
                    conditions.append('DATE(e.data_devolucao) = ?')
                    params.append(filtros['data_devolucao'])
                if conditions:
                    query += ' WHERE ' + ' AND '.join(conditions)

            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            conn.close()
