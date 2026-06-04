"""
MÓDULO DE PREPROCESAMIENTO Y NORMALIZACIÓN
Ubicación: src/preprocessor.py

Contiene las funciones estandarizadas de limpieza para homogeneizar nombres
de LPs entrantes y registros internos de la base de datos de inversión.
"""

import re
import unicodedata
import pandas as pd
from src.config import Config
from pathlib import Path

class LPNamePreprocessor:
    
    @staticmethod
    def clean_name(name: str) -> str:
        if not isinstance(name, str) or pd.isna(name):
            return ""
        
        # 1. Pasar a mayúsculas
        text = name.strip().upper()
        
        # --- NUEVO PASO SENIOR: NORMALIZACIÓN UNICODE ---
        # Remueve acentos, tildes y diéresis (ej. 'försäkring' -> 'FORSAKRING')
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        
        # 2. Sanitizar comillas externas
        text = re.sub(r'^["\']+|["\']+$', '', text)
        
        # 3. Canónizar sufijos financieros (L.P., L.L.C., S.A., S.C.S.p.)
        text = re.sub(r'\bL\s*\.\s*P\s*\.\b|\bL\s*\.\s*P\b', 'LP', text)
        text = re.sub(r'\bL\s*\.\s*L\s*\.\s*C\s*\.\b|\bL\s*\.\s*L\s*\.\s*C\b', 'LLC', text)
        text = re.sub(r'\bS\s*\.\s*A\s*\.\b|\bS\s*\.\s*A\b', 'SA', text)
        text = re.sub(r'\bS\s*\.\s*C\s*\.\s*S\s*\.\s*P\s*\.\b|\bS\s*\.\s*C\s*\.\s*S\s*\.\s*P\b', 'SCSP', text)
        
        # 4. Reducir espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    @classmethod
    def load_and_preprocess_db(cls, file_path: Path = None) -> pd.DataFrame:
        """
        Carga la base de datos interna estructurada (Capital_Calls_DB.csv)
        y genera una nueva columna procesada optimizada para la indexación léxica y vectorial.
        Mantiene intacta la metadata original del DataFrame.
        
        Args:
            file_path: Ruta alternativa del CSV. Si es None, emplea la configurada por defecto.
            
        Returns:
            DataFrame de Pandas enriquecido con la columna 'LP_Name_Clean'.
        """
        target_path = file_path or Config.CSV_PATH
        
        if not target_path.exists():
            raise FileNotFoundError(
                f"ERROR DE ARCHIVO: No se localizó la base de datos en la ruta esperada: {target_path}. "
                f"Asegúrese de ubicar el archivo 'Capital_Calls_DB.csv' dentro de la carpeta 'data/'."
            )
            
        # Cargar manteniendo tipos string para las columnas de identidades financieras
        #df = pd.read_csv(target_path, dtype={'LP Name': str})
        df = pd.read_csv(target_path, dtype={'LP Name': str}, on_bad_lines='skip')
        
        if 'LP Name' not in df.columns:
            raise KeyError(
                "ERROR DE ESQUEMA: El archivo CSV cargado no contiene la columna obligatoria 'LP Name'."
            )
            
        # Generar la columna normalizada para usar en la indexación sin alterar los datos fuente
        df['LP_Name_Clean'] = df['LP Name'].apply(cls.clean_name)
        
        return df