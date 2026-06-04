"""
INTERFAZ WEB UI/UX (STREAMLIT)
Ubicación: raíz del proyecto (app.py)

Este script despliega una aplicación web profesional que integra el motor 
de Entity Resolution y el Agente de Onboarding, proporcionando una interfaz 
visual y amigable para el analista bancario.
"""

import streamlit as st
import time
from src.rag_pipeline import EntityResolutionPipeline
from src.enrichment_agent import EnrichmentAgent
from src.indexer import DBIndexer

# =========================================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================================
st.set_page_config(
    page_title="Entity Resolution | Banca de Inversión",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# INICIALIZACIÓN DE MODELOS (CACHÉ)
# Utilizamos st.cache_resource para cargar los LLMs y el Vectorstore solo 
# una vez al arrancar la app, haciendo que la interfaz sea ultrarrápida.
# =========================================================================
@st.cache_resource(show_spinner=False)
def load_ai_systems():
    # 1. Asegurar que la base de datos vectorial existe
    indexer = DBIndexer()
    try:
        indexer.load_indices()
    except FileNotFoundError:
        indexer.build_and_save_indices()
    
    # 2. Cargar Pipelines
    rag = EntityResolutionPipeline()
    agent = EnrichmentAgent()
    return rag, agent

# =========================================================================
# DISEÑO DE LA INTERFAZ (UI)
# =========================================================================
def main():
    # --- BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=80)
        st.title("Panel de Control")
        st.markdown("---")
        st.info("🤖 **Arquitectura Activa:**\n\nSistema Multiagente Híbrido (RAG + Web Search Agent)")
        st.markdown("**Reglas de Negocio:**")
        st.markdown("- **Confidence Threshold:** `0.85`")
        st.markdown("- **Motor Reranking:** `FlashRank`")
        st.markdown("- **Embeddings:** `HuggingFace Local`")
        
    # --- ÁREA PRINCIPAL ---
    st.title("🏦 Entity Resolution & Onboarding AI")
    st.markdown("""
    Valida las solicitudes de **Capital Calls** entrantes contra la base de datos interna. 
    Si la entidad es desconocida o existe riesgo de falso positivo, nuestro **Agente de Enriquecimiento** investigará en tiempo real para generar un borrador de alta.
    """)
    st.markdown("---")

    # Carga silenciosa de los modelos
    with st.spinner("Inicializando motores de IA..."):
        rag_pipeline, enrichment_agent = load_ai_systems()

    # --- INPUT DEL USUARIO ---
    lp_input = st.text_input(
        "📝 Ingrese el nombre del Limited Partner (LP):", 
        placeholder="Ej: BNP Paribas, Border to Coast Bedfordshire Fund II, Andreessen Horowitz..."
    )

    # --- BOTÓN DE EJECUCIÓN ---
    if st.button("🔍 Iniciar Análisis de Entidad", type="primary", use_container_width=True):
        if not lp_input.strip():
            st.error("Por favor, introduzca un nombre válido.")
            return

        # 1. FASE DE RESOLUCIÓN INTERNA (RAG)
        st.markdown("### 1️⃣ Análisis de Base de Datos Interna")
        with st.spinner("Comparando semántica, léxico y series contra la base corporativa..."):
            start_time = time.time()
            rag_result = rag_pipeline.resolve_entity(lp_input)
            elapsed_time = time.time() - start_time

        # Tarjetas de Métricas (Dashboard)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Status Match", "Encontrado" if rag_result["is_match"] else "No Encontrado")
        col2.metric("Score Confianza", f"{rag_result['confidence_score']:.2f}")
        col3.metric("Revisión Manual", "Requerida ⚠️" if rag_result["trigger_human_review"] else "No necesaria ✅")
        col4.metric("Latencia", f"{elapsed_time:.2f} s")

        # Lógica de decisión de UI
        if rag_result["is_match"] and not rag_result["trigger_human_review"]:
            st.success(f"**Entidad validada internamente:** {rag_result['resolved_name']}")
            with st.expander("Ver Metadata Interna Extraída"):
                st.json(rag_result["metadata_extracted"])
            st.stop() # Finaliza el flujo aquí si todo está perfecto
            
        else:
            st.warning("⚠️ **Alerta del Sistema:** El umbral de confianza es bajo o la entidad no existe. Se requiere protocolo de alta.")
            
            st.markdown("---")
            
            # 2. FASE DE ENRIQUECIMIENTO (AGENTE WEB)
            st.markdown("### 2️⃣ Agente de Onboarding (Investigación Externa)")
            with st.spinner("Agente de IA conectándose a internet para rastrear la huella financiera (Tavily)..."):
                enrich_result = enrichment_agent.run_enrichment(lp_input)
            
            if enrich_result.get("enrichment_success"):
                st.success("✅ Datos financieros encontrados. Borrador de alta listo para revisión del analista.")
                
                # Presentación elegante de los datos propuestos
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    st.markdown("**📌 Nombre Oficial Propuesto:**")
                    st.info(enrich_result.get('proposed_official_name'))
                    st.markdown("**🌍 País Sede:**")
                    st.info(enrich_result.get('country'))
                with e_col2:
                    st.markdown("**💼 Tipo de Inversor:**")
                    st.info(enrich_result.get('investor_type'))
                    st.markdown("**📄 Resumen Corporativo:**")
                    st.info(enrich_result.get('description_summary'))
                    
                with st.expander("Ver carga útil (Payload) JSON para Inserción en Base de Datos"):
                    st.json(enrich_result)
            else:
                st.error("❌ El agente no pudo verificar la existencia de esta entidad en internet. Posible entidad fantasma o fraude. Remitir al departamento de Compliance.")

if __name__ == "__main__":
    main()