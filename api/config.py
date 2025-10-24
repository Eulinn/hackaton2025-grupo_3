import os
from sqlalchemy import create_engine

class Config:
    # Ollama
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    # Sugestão: para melhor Text-to-SQL, teste 'sqlcoder:7b' no Ollama
    MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:1b")
    
    # Database Schema JSON
    SCHEMA_JSON_PATH = "schema_descriptions.json"
    
    # PostgreSQL Database Configuration
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'hackatonrerun'
    DB_USER = 'postgres'
    DB_PASSWORD = 'root'
    
    # App
    DEBUG = True
    PORT = 5000
    
    @classmethod
    def get_database_url(cls):
        """Constrói URL de conexão PostgreSQL"""
        # Usa o driver pg8000 (puro Python) para evitar problemas de DLL no Windows
        return f"postgresql+pg8000://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

# Configuração do SQLAlchemy para PostgreSQL
try:
    engine = create_engine(Config.get_database_url(), echo=False)
    print(f"✅ Configuração PostgreSQL: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
except Exception as e:
    print(f"⚠️ Erro na configuração do banco: {e}")
    engine = None