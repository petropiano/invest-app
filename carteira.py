import sqlite3
import database

def adicionar_posicao(id_usuario, id_ativo, valor_investido, data_compra):
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
        INSERT INTO posicoes (id_usuario, id_ativo, valor_investido, data_compra)
        VALUES (?, ?, ?, ?)
        """
        
        cursor.execute(sql_insert, (id_usuario, id_ativo, valor_float, data_compra))
        
        db.commit()
        db.close()
        
        return True

    except Exception:
        return False
