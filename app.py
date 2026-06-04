"""
INTERFAZ WEB UI/UX (STREAMLIT)
Ubicación: raíz del proyecto (app.py)

Este script despliega una aplicación web profesional que integra el motor 
de Entity Resolution y el Agente de Onboarding, proporcionando una interfaz 
visual y amigable para el analista bancario.
"""

import streamlit as st
import time
import pandas as pd
from src.config import Config
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
# =========================================================================
@st.cache_resource(show_spinner=False)
def load_ai_systems():
    indexer = DBIndexer()
    try:
        indexer.load_indices()
    except FileNotFoundError:
        indexer.build_and_save_indices()
    
    rag = EntityResolutionPipeline()
    agent = EnrichmentAgent()
    return rag, agent

# =========================================================================
# DISEÑO DE LA INTERFAZ (UI)
# =========================================================================
def main():
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=80)
        st.title("Panel de Control")
        st.markdown("---")
        st.info("🤖 **Arquitectura Activa:**\n\nSistema Multiagente Híbrido (RAG + Web Search Agent)")
        st.markdown("**Reglas de Negocio:**")
        st.markdown("- **Confidence Threshold:** `0.85`")
        st.markdown("- **Motor Reranking:** `FlashRank`")
        st.markdown("- **Embeddings:** `HuggingFace Local`")
        
    st.title("🏦 Entity Resolution & Onboarding AI")
    st.markdown("Valida las solicitudes de **Capital Calls** entrantes contra la base de datos interna.")
    st.markdown("---")

    # Carga silenciosa de los modelos
    with st.spinner("Inicializando motores de IA..."):
        rag_pipeline, enrichment_agent = load_ai_systems()

    # =========================================================================
    # GESTIÓN DEL ESTADO DE LA SESIÓN (Solución al refresco de pantalla)
    # =========================================================================
    if "analisis_completado" not in st.session_state:
        st.session_state.analisis_completado = False
    if "rag_result" not in st.session_state:
        st.session_state.rag_result = None
    if "enrich_result" not in st.session_state:
        st.session_state.enrich_result = None
    if "lp_input_guardado" not in st.session_state:
        st.session_state.lp_input_guardado = ""

    # --- INPUT DEL USUARIO ---
    lp_input = st.text_input(
        "📝 Ingrese el nombre del Limited Partner (LP):", 
        placeholder="Ej: BNP Paribas, Andreessen Horowitz..."
    )

    # --- BOTÓN DE EJECUCIÓN (Solo guarda los resultados en memoria) ---
    if st.button("🔍 Iniciar Análisis de Entidad", type="primary", use_container_width=True):
        if not lp_input.strip():
            st.error("Por favor, introduzca un nombre válido.")
        else:
            # 1. Ejecutamos y guardamos el RAG en memoria
            with st.spinner("Comparando semántica, léxico y series contra la base corporativa..."):
                st.session_state.rag_result = rag_pipeline.resolve_entity(lp_input)
                st.session_state.lp_input_guardado = lp_input
                
            # 2. Si falla el RAG, ejecutamos y guardamos el Agente en memoria
            if not st.session_state.rag_result["is_match"] or st.session_state.rag_result["trigger_human_review"]:
                with st.spinner("Agente de IA conectándose a internet para rastrear huella financiera..."):
                    st.session_state.enrich_result = enrichment_agent.run_enrichment(lp_input)
            else:
                st.session_state.enrich_result = None
                
            st.session_state.analisis_completado = True

    # =========================================================================
    # MOSTRAR RESULTADOS (Lee de la memoria, independiente de los clics)
    # =========================================================================
    if st.session_state.analisis_completado:
        st.markdown("### 1️⃣ Análisis de Base de Datos Interna")
        
        # Tarjetas de Métricas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Status Match", "Encontrado" if st.session_state.rag_result["is_match"] else "No Encontrado")
        col2.metric("Score Confianza", f"{st.session_state.rag_result['confidence_score']:.2f}")
        col3.metric("Revisión Manual", "Requerida ⚠️" if st.session_state.rag_result["trigger_human_review"] else "No necesaria ✅")
        col4.metric("Entidad Analizada", st.session_state.lp_input_guardado)

        if st.session_state.rag_result["is_match"] and not st.session_state.rag_result["trigger_human_review"]:
            st.success(f"**Entidad validada internamente:** {st.session_state.rag_result['resolved_name']}")
            with st.expander("Ver Metadata Interna Extraída"):
                st.json(st.session_state.rag_result["metadata_extracted"])
                
        else:
            st.warning("⚠️ **Alerta del Sistema:** El umbral de confianza es bajo o la entidad no existe. Se requiere protocolo de alta.")
            st.markdown("---")
            
            # --- FASE 2: AGENTE ---
            if st.session_state.enrich_result:
                st.markdown("### 2️⃣ Agente de Onboarding (Investigación Externa)")
                
                if st.session_state.enrich_result.get("enrichment_success"):
                    st.success("✅ Datos financieros encontrados. Borrador de alta listo para revisión del analista.")
                    
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        st.markdown("**📌 Nombre Oficial Propuesto:**")
                        st.info(st.session_state.enrich_result.get('proposed_official_name'))
                        st.markdown("**🌍 País Sede:**")
                        st.info(st.session_state.enrich_result.get('country'))
                    with e_col2:
                        st.markdown("**💼 Tipo de Inversor:**")
                        st.info(st.session_state.enrich_result.get('investor_type'))
                        st.markdown("**📄 Resumen Corporativo:**")
                        st.info(st.session_state.enrich_result.get('description_summary'))
                    
                    # --- BOTÓN DE ALTA CORPORATIVA ---
                    st.markdown("---")
                    st.markdown("### 🛠️ Acción Requerida")
                    if st.button("✅ Aprobar Alta e Insertar en Base de Datos", type="primary"):
                        with st.spinner("Guardando en BBDD corporativa y reentrenando índices vectoriales..."):
                            
                            ## 1. Crear registro
                            nuevo_registro = pd.DataFrame([{
                                "LP Name": st.session_state.enrich_result.get('proposed_official_name'),
                                "Investor Type": st.session_state.enrich_result.get('investor_type'),
                                "Country": st.session_state.enrich_result.get('country'),
                                "S&P": "NR",
                                "Moody's": "NR"
                            }])
                            
                            # 2. Insertar en CSV de forma SEGURA (Evita errores de saltos de línea)
                            # Leemos la BBDD actual, concatenamos la nueva fila y sobreescribimos limpiamente
                            df_actual = pd.read_csv(Config.CSV_PATH, on_bad_lines='skip')
                            df_actualizado = pd.concat([df_actual, nuevo_registro], ignore_index=True)
                            df_actualizado.to_csv(Config.CSV_PATH, index=False)
                            
                            # 3. Re-entrenar Indexer
                            indexer = DBIndexer()
                            indexer.build_and_save_indices()
                            
                            # 4. Limpiar caché para forzar la recarga del cerebro de IA
                            st.cache_resource.clear()
                            
                            # 5. Limpiar la memoria de la sesión
                            st.session_state.analisis_completado = False
                            st.session_state.rag_result = None
                            st.session_state.enrich_result = None
                            
                        st.success("🎉 ¡Operación Exitosa! La entidad ha sido dada de alta. Búsquela nuevamente para validar.")
                        st.balloons()
                else:
                    st.error("❌ El agente no pudo verificar la existencia de esta entidad en internet. Remitir al departamento de Compliance.")

if __name__ == "__main__":
    main()