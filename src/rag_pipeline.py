"""
MÓDULO DEL PIPELINE RAG (ENTITY RESOLUTION)
Ubicación: src/rag_pipeline.py

Orquesta la recuperación híbrida, el reranking y la cadena (Chain) del LLM
aplicando las reglas de negocio estrictas para validación de LPs.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_classic.retrievers import EnsembleRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors import FlashrankRerank

from src.config import Config
from src.indexer import DBIndexer
from src.fallback_factory import LLMFactory
from src.preprocessor import LPNamePreprocessor


# =========================================================================
# 1. ESQUEMA DE SALIDA ESTRUCTURADO (Pydantic)
# =========================================================================
class EntityResolutionOutput(BaseModel):
    """
    Define y fuerza la estructura del JSON que devolverá el LLM, eliminando
    el riesgo de fallos de parsing.
    """
    resolved_name: str = Field(
        description="Nombre oficial exacto del LP según la base de datos si hay match. Si no hay, 'null'."
    )
    is_match: bool = Field(
        description="True si se encontró una coincidencia inequívoca, False en caso contrario."
    )
    confidence_score: float = Field(
        description="Nivel de confianza de la resolución (0.0 a 1.0)."
    )
    trigger_human_review: bool = Field(
        description="REGLA ESTRICTA: Debe ser True OBLIGATORIAMENTE si confidence_score < 0.85 o si existen múltiples candidatos muy similares sin desempate obvio."
    )
    metadata_extracted: dict = Field(
        description="Diccionario con country, investor_type, sp_rating y moodys_rating recuperados del contexto. Vacío si no hay match."
    )


# =========================================================================
# 2. CLASE ORQUESTADORA
# =========================================================================
class EntityResolutionPipeline:
    
    def __init__(self):
        self.llm = LLMFactory.get_llm()
        self.retriever = self._setup_retriever()
        self.chain = self._setup_chain()
        
    def _setup_retriever(self) -> ContextualCompressionRetriever:
        """
        Configura la recuperación híbrida (BM25 + FAISS) y le aplica una 
        capa de Reranking (Flashrank) para devolver únicamente los mejores contextos.
        """
        indexer = DBIndexer()
        vectorstore, bm25_retriever = indexer.load_indices()
        
        # 1. Buscador Semántico
        faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": Config.RETRIEVAL_K})
        
        # 2. Ensemble Retriever (Fusión RRF)
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, faiss_retriever],
            weights=[Config.ENSEMBLE_WEIGHT_BM25, Config.ENSEMBLE_WEIGHT_VECTOR]
        )
        
        # 3. Reranker (Capa de compresión para alta precisión)
        # Reducimos los candidatos al top 3 definitivo antes de enviarlos al LLM
        compressor = FlashrankRerank(top_n=3)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=ensemble_retriever
        )
        
        return compression_retriever
    
    @staticmethod
    def _format_docs(docs) -> str:
        """Formatea los documentos recuperados para inyectarlos en el prompt."""
        formatted = []
        for d in docs:
            # Usamos el nombre original de la metadata para que el modelo lo vea intacto
            original = d.metadata.get('original_name', d.page_content)
            meta = {k: v for k, v in d.metadata.items() if k != 'original_name'}
            formatted.append(f"Entity: {original} | Data: {meta}")
        return "\n".join(formatted)
        
    def _setup_chain(self):
        """Construye la cadena (Chain) de LangChain."""
        
        # Parser asociado al modelo Pydantic
        parser = JsonOutputParser(pydantic_object=EntityResolutionOutput)
        
        template = """Eres un sistema experto en Entity Resolution para banca de inversión.
Tu tarea es comparar el nombre del Limited Partner (LP) entrante (Query) contra el contexto proporcionado por la base de datos interna.

CONTEXTO INTERNO DISPONIBLE:
{context}

QUERY DE ENTRADA (LP a resolver):
{query}

REGLAS ESTRICTAS DE NEGOCIO:
1. Analiza si el LP de entrada corresponde a una entidad del contexto (ignorando errores tipográficos, diferencias entre 'L.P.' y 'LP', o diéresis).
2. Si la entidad entrante difiere por números romanos o series (ej. 'Fund II' vs 'Fund III'), SON ENTIDADES DISTINTAS. is_match debe ser False.
3. Evalúa la correspondencia para calcular el confidence_score.
4. REGLA CRÍTICA: Si el confidence_score es INFERIOR A 0.85, debes forzar OBLIGATORIAMENTE el campo "trigger_human_review" a true.
5. Devuelve única y exclusivamente el JSON sin texto adicional (nada de backticks de markdown).

{format_instructions}
"""
        prompt = ChatPromptTemplate.from_template(template)
        
        # Pipeline = Recuperar y formatear docs -> Construir Prompt -> LLM -> Parsear JSON
        chain = (
            {
                "context": self.retriever | self._format_docs, 
                "query": RunnablePassthrough(),
                "format_instructions": lambda _: parser.get_format_instructions()
            }
            | prompt
            | self.llm
            | parser
        )
        
        return chain
        
    def resolve_entity(self, lp_name: str) -> Dict[str, Any]:
        """
        Método de entrada para resolver una entidad.
        Aplica la limpieza previa determinista al nombre (Query) para maximizar 
        el éxito en el ensemble retriever, y luego ejecuta el RAG.
        """
        # Paso 1: Normalizamos la query (igual que hicimos al indexar)
        clean_query = LPNamePreprocessor.clean_name(lp_name)
        
        # Paso 2: Invocamos la cadena
        print(f"\n🔍 Resolviendo Entidad Original: '{lp_name}' (Query procesada: '{clean_query}')...")
        result = self.chain.invoke(clean_query)
        
        return result