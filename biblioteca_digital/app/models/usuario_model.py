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
        try:
            cursor = conn.cursor()
            # Check if email already exists to avoid IntegrityError in tests or production
            cursor.execute('SELECT id FROM usuarios WHERE email = ?', (self.email,))
            if cursor.fetchone():
                return
                
            cursor.execute('''
                INSERT INTO usuarios (nome, email, senha_hash, papel)
                VALUES (?, ?, ?, ?)
            ''', (self.nome, self.email, self.senha_hash, self.papel))
            conn.commit()
            self.id = cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def buscar_por_email(email):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
            row = cursor.fetchone()
            if row:
                return UsuarioModel(row['nome'], row['email'], row['senha_hash'], row['papel'], row['id'])
        finally:
            conn.close()
        return None
