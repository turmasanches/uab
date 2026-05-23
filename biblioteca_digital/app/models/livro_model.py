from app.database import conectar_db

class LivroModel:
    def __init__(self, titulo, autor, categoria, status='DISPONIVEL', id=None):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.status = status

    def salvar(self):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO livros (titulo, autor, categoria, status)
            VALUES (?, ?, ?, ?)
        ''', (self.titulo, self.autor, self.categoria, self.status))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos(filtros=None):
        conn = conectar_db()
        cursor = conn.cursor()
        query = 'SELECT * FROM livros'
        params = []
        if filtros:
            conditions = []
            if 'titulo' in filtros and filtros['titulo']:
                conditions.append('titulo LIKE ?')
                params.append(f"%{filtros['titulo']}%")
            if 'autor' in filtros and filtros['autor']:
                conditions.append('autor LIKE ?')
                params.append(f"%{filtros['autor']}%")
            if 'categoria' in filtros and filtros['categoria']:
                conditions.append('categoria LIKE ?')
                params.append(f"%{filtros['categoria']}%")
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [LivroModel(row['titulo'], row['autor'], row['categoria'], row['status'], row['id']) for row in rows]

    @staticmethod
    def buscar_por_id(id):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM livros WHERE id = ?', (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return LivroModel(row['titulo'], row['autor'], row['categoria'], row['status'], row['id'])
        return None

    def atualizar_status(self, novo_status):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE livros SET status = ? WHERE id = ?', (novo_status, self.id))
        conn.commit()
        conn.close()
        self.status = novo_status
