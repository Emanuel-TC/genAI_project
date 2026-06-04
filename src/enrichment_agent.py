"""
MÓDULO DE ENRIQUECIMIENTO WEB (ONBOARDING)
Ubicación: src/enrichment_agent.py

Este agente entra en acción cuando el Entity Resolution falla. 
Utiliza Tavily Search para investigar a la entidad en tiempo real 
y estructurar un borrador de alta para la base de datos.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults

from src.fallback_factory import LLMFactory

# =========================================================================
# 1. ESQUEMA DE SALIDA PARA EL NUEVO LP
# =========================================================================
class LPEnrichmentOutput(BaseModel):
    proposed_official_name: str = Field(
        description="Nombre oficial legal de la entidad encontrado en la web."
    )
    country: str = Field(
        description="País de origen o sede principal (ej. 'United States', 'Spain', 'Unknown')."
    )
    investor_type: str = Field(
        description="Clasificación financiera inferida (ej. 'Pension Fund', 'Asset Manager', 'SWF', 'Venture Capital', 'Unknown')."
    )
    description_summary: str = Field(
        description="Breve resumen de 1 o 2 líneas sobre a qué se dedica la entidad."
    )
    enrichment_success: bool = Field(
        description="True si se encontró información financiera útil, False si la entidad no parece existir o no hay datos relevantes."
    )
    sp_rating: str = Field(
        description="Rating S&P sugerido si se menciona, o 'NR' (Not Rated)."
        )
    moodys_rating: str = Field(
        description="Rating Moody's sugerido si se menciona, o 'NR'."
        )
    confidence_score: float = Field(
        description="Nivel de confianza (0.0 a 1.0) de la información recopilada en la web."
        )
    justification: str = Field(
        description="Justificación de los valores sugeridos basándose en los textos leídos."
        )
    sources: list[str] = Field(
        description="Lista de URLs utilizadas como referencia."
        )

# =========================================================================
# 2. AGENTE DE BÚSQUEDA Y EXTRACCIÓN
# =========================================================================
class EnrichmentAgent:
    def __init__(self):
        # Reutilizamos nuestra fábrica para que herede Groq o DeepSeek automáticamente
        self.llm = LLMFactory.get_llm()
        
        # Herramienta de búsqueda web (max_results=3 es suficiente para no gastar muchos tokens)
        self.search_tool = TavilySearchResults(max_results=3)
        self.parser = JsonOutputParser(pydantic_object=LPEnrichmentOutput)

    def run_enrichment(self, lp_name: str) -> Dict[str, Any]:
        print(f"🌐 [Tavily Search] Investigando la huella digital de: '{lp_name}'...")
        
        # 1. Ejecutar la búsqueda en internet optimizada para banca
        search_query = f"{lp_name} investment firm limited partner headquarters"
        try:
            web_results = self.search_tool.invoke({"query": search_query})
        except Exception as e:
            print(f"⚠️ Error al conectar con internet: {e}")
            web_results = "No internet access available."

        # 2. Prompt Template para el Agente
        template = """Eres un Analista de Onboarding en un Banco de Inversión.
El sistema de resolución de entidades no encontró al inversor "{lp_name}" en la base de datos.
Tu tarea es leer los siguientes resultados de una búsqueda web en tiempo real y extraer la información para crear un BORRADOR DE ALTA.

RESULTADOS DE LA BÚSQUEDA WEB:
{web_context}

INSTRUCCIONES ESTRICTAS:
1. Extrae el nombre oficial, país de la sede principal y el tipo de inversor.
2. Escribe un resumen de máximo 2 líneas.
3. Si los resultados no tienen sentido o se refieren a algo que no es una entidad corporativa/financiera, marca "enrichment_success" como false y pon "Unknown" en el resto.
4. Devuelve ÚNICAMENTE un JSON válido siguiendo el formato.

{format_instructions}
"""
        prompt = ChatPromptTemplate.from_template(template)
        
        # 3. Orquestación de la cadena
        chain = prompt | self.llm | self.parser
        
        print("🧠 [LLM] Analizando y estructurando resultados web...")
        result = chain.invoke({
            "lp_name": lp_name,
            "web_context": web_results,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        return result