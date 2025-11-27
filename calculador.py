import yfinance as yf
import sqlite3
import database
import requests
from datetime import datetime, timedelta

def verificar_api_bcb():
    url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados/ultimos/10?formato=json'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return True
    except Exception:
        return False

def get_preco_historico(ticker_simbolo, data_compra_str):
    ticker_sa = ticker_simbolo + ".SA"
    
    try:
        data_compra = datetime.strptime(data_compra_str, '%Y-%m-%d').date()
        data_seguinte = data_compra + timedelta(days=2)
        
        ticker_data = yf.Ticker(ticker_sa)
        
        hist = ticker_data.history(start=data_compra_str, end=data_seguinte.strftime('%Y-%m-%d'), interval="1d")
        
        if hist.empty:
            return None
            
        return hist['Close'].iloc[0]
        
    except Exception as e:
        print(f"Erro ao buscar preço histórico de {ticker_sa}: {e}")
        return None

def get_dados_cdi(data_inicio_str, data_fim_str):
    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').strftime('%d/%m/%Y')
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except ValueError:
        return []

    url_api = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}'
    
    try:
        response = requests.get(url_api)
        response.raise_for_status()
        dados = response.json()
        
        if not dados:
            return []
            
        return dados
    except Exception as e:
        print(f"Erro ao buscar API do BCB: {e}")
        return []
