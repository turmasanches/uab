from app.database import conectar_db
from functools import lru_cache

@lru_cache(maxsize=32)
def _get_livros_from_db(filtros_tuple):
    conn = conectar_db()
    try:
        cursor = conn.cursor()
        query = 'SELECT * FROM livros'
        params = []
        filtros = dict(filtros_tuple)
        if filtros:
            conditions = []
            for key, value in filtros.items():
                if value:
                    if key == 'id':
                        conditions.append(f"{key} = ?")
                        params.append(value)
                    else:
                        conditions.append(f"{key} LIKE ?")
                        params.append(f"%{value}%")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [LivroModel(row['titulo'], row['autor'], row['categoria'], row['status'], row['id']) for row in rows]
    finally:
        conn.close()

class LivroModel:
    def __init__(self, titulo, autor, categoria, status='DISPONIVEL', id=None):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.status = status

    def salvar(self):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO livros (titulo, autor, categoria, status)
                VALUES (?, ?, ?, ?)
            ''', (self.titulo, self.autor, self.categoria, self.status))
            conn.commit()
            self.id = cursor.lastrowid
            LivroModel.clear_cache()
        finally:
            conn.close()

    @staticmethod
    def buscar_todos(filtros=None):
        if filtros is None:
            filtros = {}
        # Convert to a stable hashable type
        filtros_tuple = tuple(sorted(filtros.items()))
        return _get_livros_from_db(filtros_tuple)

    @staticmethod
    def clear_cache():
        _get_livros_from_db.cache_clear()

    @staticmethod
    def buscar_por_id(id):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM livros WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return LivroModel(row['titulo'], row['autor'], row['categoria'], row['status'], row['id'])
        finally:
            conn.close()
        return None

    def atualizar_status(self, novo_status):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE livros SET status = ? WHERE id = ?', (novo_status, self.id))
            conn.commit()
            self.status = novo_status
            LivroModel.clear_cache()
        finally:
            conn.close()
