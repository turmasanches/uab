from app.database import conectar_db

class UsuarioModel:
    def __init__(self, nome, email, senha_hash, papel, id=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.papel = papel

    def salvar(self):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha_hash, papel)
            VALUES (?, ?, ?, ?)
        ''', (self.nome, self.email, self.senha_hash, self.papel))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_por_email(email):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return UsuarioModel(row['nome'], row['email'], row['senha_hash'], row['papel'], row['id'])
        return None

    @staticmethod
    def buscar_por_id(id):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE id = ?', (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return UsuarioModel(row['nome'], row['email'], row['senha_hash'], row['papel'], row['id'])
        return None
