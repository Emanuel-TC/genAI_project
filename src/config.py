"""
MÓDULO DE CONFIGURACIÓN CENTRALIZADA
Ubicación: src/config.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # RUTAS
    SRC_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = SRC_DIR.parent
    DATA_DIR = PROJECT_ROOT / "data"
    VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"
    CSV_PATH = DATA_DIR / "Capital_Calls_DB.csv"
    
    # INTERRUPTOR MULTI-PROVEEDOR
    # Valores admitidos: "openai" | "groq" | "google" | "deepseek"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower().strip()
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # Aceptamos tanto GOOGLE_API_KEY como GEMINI_API_KEY
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    # Keys Operativas (Observabilidad y Herramientas)
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Modelos
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    LLM_TEMPERATURE = 0.0
    
    # HIPERPARÁMETROS RAG
    EMBEDDING_MODEL = "text-embedding-3-small"
    RETRIEVAL_K = 5
    ENSEMBLE_WEIGHT_VECTOR = 0.5
    ENSEMBLE_WEIGHT_BM25 = 0.5
    CONFIDENCE_THRESHOLD = 0.85

    @classmethod
    def validate_config(cls) -> None:
        valid_providers = ["openai", "groq", "google", "deepseek"]
        if cls.LLM_PROVIDER not in valid_providers:
            raise ValueError(f"ERROR: LLM_PROVIDER '{cls.LLM_PROVIDER}' no soportado. Usa: {valid_providers}")
            
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("Falta OPENAI_API_KEY en .env")
        elif cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            raise ValueError("Falta GROQ_API_KEY en .env")
        elif cls.LLM_PROVIDER == "google" and not cls.GOOGLE_API_KEY:
            raise ValueError("Falta GEMINI_API_KEY o GOOGLE_API_KEY en .env")
        elif cls.LLM_PROVIDER == "deepseek" and not cls.DEEPSEEK_API_KEY:
            raise ValueError("Falta DEEPSEEK_API_KEY en .env")