import sqlite3
import database

def adicionar_posicao(id_usuario, id_ativo, valor_investido, data_compra, tipo_rendimento=None, taxa=0.0):
    try:
        if not id_usuario or not id_ativo:
            return False
            
        valor_float = float(valor_investido)
        if valor_float <= 0:
            return False
            
        if not data_compra:
            return False

        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        
        sql_insert = """
        INSERT INTO posicoes (id_usuario, id_ativo, valor_investido, data_compra, tipo_rendimento, taxa)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(sql_insert, (id_usuario, id_ativo, valor_float, data_compra, tipo_rendimento, taxa))
        
        db.commit()
        db.close()
        
        return True

    except Exception:
        return False

def get_posicao_por_id(id_posicao):
    try:
        db = sqlite3.connect(database.DB_NOME)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        
        sql = "SELECT * FROM posicoes WHERE id = ?"
        cursor.execute(sql, (id_posicao,))
        posicao = cursor.fetchone()
        
        db.close()
        return posicao
    except Exception:
        return None

def editar_posicao(id_posicao, novo_valor, nova_data):
    try:
        valor_float = float(novo_valor)
        if valor_float <= 0 or not nova_data:
            return False
            
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        
        sql_update = """
        UPDATE posicoes
        SET valor_investido = ?, data_compra = ?
        WHERE id = ?
        """
        
        cursor.execute(sql_update, (valor_float, nova_data, id_posicao))
        db.commit()
        db.close()
        return True
    except Exception:
        return False

def deletar_posicao_web(id_posicao, id_usuario_requisitante):
    try:
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        
        cursor.execute("SELECT id_usuario FROM posicoes WHERE id = ?", (id_posicao,))
        resultado = cursor.fetchone()
        
        if not resultado:
            db.close()
            return False
            
        dono_da_posicao = resultado[0]
        
        if dono_da_posicao != id_usuario_requisitante:
            db.close()
            return False
            
        cursor.execute("DELETE FROM posicoes WHERE id = ?", (id_posicao,))
        db.commit()
        db.close()
        return True
        
    except Exception:
        return False
