import sqlite3
import database
from werkzeug.security import generate_password_hash

def cadastrar_usuario(nome_digitado, email_digitado, senha_digitada):
    nome = nome_digitado.strip().capitalize()
    email = email_digitado.strip().lower()
    
    if not nome or not email or not senha_digitada:
        return False
        
    if "@" not in email or "." not in email:
        return False
    
    hash_senha = generate_password_hash(senha_digitada)

    try:
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        
        novo_usuario_sql = """
        INSERT INTO usuarios (nome, email, senha) 
        VALUES (?, ?, ?)
        """
        
        cursor.execute(novo_usuario_sql, (nome, email, hash_senha))
        
        db.commit()
        db.close()
        
        return True
        
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        return False
