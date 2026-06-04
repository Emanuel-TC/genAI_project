"""
MÓDULO DE CONFIGURACIÓN CENTRALIZADA
Ubicación: src/config.py

Gestiona las rutas del proyecto, variables de entorno, parámetros de los modelos
y las reglas de negocio estrictas para el pipeline de Entity Resolution.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env local
load_dotenv()

class Config:
    # =========================================================================
    # CONFIGURACIÓN DE RUTAS (Estructura de producción Git)
    # =========================================================================
    SRC_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = SRC_DIR.parent
    DATA_DIR = PROJECT_ROOT / "data"
    VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"
    
    # Ruta absoluta al archivo de base de datos interna (Ground Truth)
    CSV_PATH = DATA_DIR / "Capital_Calls_DB.csv"
    
    # =========================================================================
    # INTERRUPTOR MULTI-PROVEEDOR (Fallback Dinámico)
    # =========================================================================
    # Valores admitidos: "openai" | "groq" | "google"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower().strip()
    
    # API Keys desde variables de entorno
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Mapeo de Modelos específicos por Proveedor
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    
    # Temperatura forzada a cero para mitigar la variabilidad cognitiva (Cero Alucinación)
    LLM_TEMPERATURE = 0.0
    
    # =========================================================================
    # HIPERPARÁMETROS DEL PIPELINE RAG HÍBRIDO
    # =========================================================================
    # Modelo de representación vectorial por defecto
    EMBEDDING_MODEL = "text-embedding-3-small"
    
    # Número de candidatos candidatos recuperados en el primer filtro
    RETRIEVAL_K = 5
    
    # Pesos asignados para el Ensemble Retriever (Reciprocal Rank Fusion)
    ENSEMBLE_WEIGHT_VECTOR = 0.5
    ENSEMBLE_WEIGHT_BM25 = 0.5
    
    # =========================================================================
    # REGLAS ESTRICTAS DE NEGOCIO (Entity Resolution)
    # =========================================================================
    # Umbral mínimo de confianza exigido por el negocio bancario
    CONFIDENCE_THRESHOLD = 0.85

    @classmethod
    def validate_config(cls) -> None:
        """
        Valida de forma preventiva la disponibilidad de credenciales críticas
        según el proveedor seleccionado para evitar fallos en tiempo de ejecución.
        """
        valid_providers = ["openai", "groq", "google"]
        if cls.LLM_PROVIDER not in valid_providers:
            raise ValueError(
                f"ERROR CRÍTICO: LLM_PROVIDER '{cls.LLM_PROVIDER}' no es soportado. "
                f"Utilizar uno de los siguientes: {valid_providers}"
            )
            
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("ERROR DE ENTORNO: LLM_PROVIDER es 'openai' pero falto configurar OPENAI_API_KEY.")
        elif cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            raise ValueError("ERROR DE ENTORNO: LLM_PROVIDER es 'groq' pero falto configurar GROQ_API_KEY.")
        elif cls.LLM_PROVIDER == "google" and not cls.GOOGLE_API_KEY:
            raise ValueError("ERROR DE ENTORNO: LLM_PROVIDER es 'google' pero falto configurar GOOGLE_API_KEY.")