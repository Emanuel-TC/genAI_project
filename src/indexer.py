"""
MÓDULO DE INDEXACIÓN PERSISTENTE (FAISS + BM25)
Ubicación: src/indexer.py

Convierte la base de datos de LPs en un Vectorstore de FAISS y un índice léxico de BM25.
Implementa serialización local en la carpeta /vectorstore para evitar reindexar
en cada ejecución.
"""

import pickle
from pathlib import Path
from typing import Tuple

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever

from src.config import Config
from src.preprocessor import LPNamePreprocessor


class DBIndexer:
    """
    Clase encargada de transformar el DataFrame de la base de datos interna
    en una colección de documentos vectoriales y de búsqueda léxica.
    """
    
    def __init__(self):
        # Aseguramos que la carpeta de destino exista
        Config.VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
        self.faiss_path = Config.VECTORSTORE_DIR / "faiss_index"
        self.bm25_path = Config.VECTORSTORE_DIR / "bm25_index.pkl"
        
        # Inicialización Inteligente de Embeddings (Evita Crash sin API Key)
        if Config.OPENAI_API_KEY:
            from langchain_openai import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings(
                api_key=Config.OPENAI_API_KEY,
                model=Config.EMBEDDING_MODEL
            )
        else:
            print("⚠️ AVISO: No se detectó OPENAI_API_KEY. Fallback a Embeddings Locales de HuggingFace.")
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def generate_documents(self) -> list[Document]:
        """
        Carga el dataframe preprocesado y convierte cada fila en un objeto Document.
        """
        df = LPNamePreprocessor.load_and_preprocess_db()
        
        # SANEAMIENTO CRÍTICO: Rellenar NaNs para evitar excepciones en los metadatos de LangChain
        df.fillna("Unknown", inplace=True)
        
        docs = []
        for _, row in df.iterrows():
            metadata = {
                "original_name": str(row["LP Name"]),
                "investor_type": str(row["Investor Type"]),
                "country": str(row["Country"]),
                "sp_rating": str(row["S&P"]),
                "moodys_rating": str(row["Moody's"])
            }
            # El page_content será la versión limpia para facilitar el emparejamiento matemático/léxico
            doc = Document(page_content=str(row["LP_Name_Clean"]), metadata=metadata)
            docs.append(doc)
            
        return docs
        
    def build_and_save_indices(self) -> None:
        """
        Construye desde cero el Vectorstore y el índice BM25 y los guarda en disco.
        Este método solo se debe ejecutar una vez (o cuando se actualice el CSV).
        """
        docs = self.generate_documents()
        print(f"🔄 Indexando {len(docs)} Limited Partners...")
        
        # 1. Construir y Guardar FAISS (Búsqueda Semántica)
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        vectorstore.save_local(str(self.faiss_path))
        print(f"✅ FAISS index persistido en: {self.faiss_path}")
        
        # 2. Construir y Guardar BM25 (Búsqueda por Palabras Clave / Acrónimos)
        bm25_retriever = BM25Retriever.from_documents(docs)
        with open(self.bm25_path, "wb") as f:
            pickle.dump(bm25_retriever, f)
        print(f"✅ BM25 index persistido en: {self.bm25_path}")
        
    def load_indices(self) -> Tuple[FAISS, BM25Retriever]:
        """
        Carga los índices desde el disco a la memoria RAM.
        Requisito: Ejecutar build_and_save_indices() antes.
        """
        if not self.faiss_path.exists() or not self.bm25_path.exists():
            raise FileNotFoundError(
                "❌ Los índices no existen. Debes ejecutar db_indexer.build_and_save_indices() primero."
            )
            
        vectorstore = FAISS.load_local(
            str(self.faiss_path), 
            self.embeddings, 
            allow_dangerous_deserialization=True # Necesario en LangChain moderno para FAISS local
        )
        
        with open(self.bm25_path, "rb") as f:
            bm25_retriever = pickle.load(f)
            
        return vectorstore, bm25_retriever