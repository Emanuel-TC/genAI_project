"""
SCRIPT PRINCIPAL DE EJECUCIÓN Y EVALUACIÓN
Ubicación: raíz del proyecto (main.py) o notebooks/entity_resolution_run.ipynb

Este script orquesta el pipeline de Entity Resolution, inicializa las bases 
de datos vectoriales si no existen, y ejecuta una batería de pruebas (Edge Cases)
para demostrar la robustez del sistema frente al tribunal.
"""

import json
import time
from src.indexer import DBIndexer
from src.rag_pipeline import EntityResolutionPipeline

def setup_database():
    print("=== FASE 1: INICIALIZACIÓN DE LA BASE DE DATOS ===")
    indexer = DBIndexer()
    
    # Comprobamos si los índices ya existen para no recomputar embeddings innecesariamente
    try:
        indexer.load_indices()
        print("✅ Índices cargados exitosamente desde almacenamiento local (vectorstore/).\n")
    except FileNotFoundError:
        print("⚠️ Índices no encontrados. Construyendo FAISS y BM25 desde cero...")
        indexer.build_and_save_indices()
        print("\n")

def run_evaluation_suite():
    print("=== FASE 2: EVALUACIÓN DE CASOS EXTREMOS (EDGE CASES) ===")
    
    # Inicializamos el pipeline RAG. Esto leerá tu .env y cargará Groq o DeepSeek automáticamente.
    pipeline = EntityResolutionPipeline()

    # Definición de escenarios de prueba estratégicos para desafiar al LLM
    test_cases = [
        {
            "id": "Test 1: Match Exacto con Ruido Sintáctico",
            "query": "  Al Sariya Commercial Investments L.L.C. ",
            "desc": "El preprocesador limpia los espacios y normaliza L.L.C. a LLC. LangChain debe hacer match perfecto."
        },
        {
            "id": "Test 2: Falso Positivo por Serie/Fondo Distinto",
            "query": "Border to Coast Bedfordshire Fund II LP",
            "desc": "Existe 'Border to Coast Bedfordshire LP' en la DB. Al añadir 'Fund II', es una entidad legal distinta. Debe rechazarlo y pedir revisión."
        },
        {
            "id": "Test 3: Falso Positivo por Diferencia Geográfica",
            "query": "Caisse Regionale Crédit Agricole Mutuel de Paris",
            "desc": "Existe '... Mutuel des Côtes d'Armor' en la DB. El cambio de ciudad implica subsidiaria distinta. Debe rechazarlo."
        },
        {
            "id": "Test 4: Entidad Totalmente Inexistente",
            "query": "Tech Ventures Capital Innovacion SA",
            "desc": "No existe nada semánticamente parecido en el CSV. El modelo debe asignar is_match = False y devolver metadata nula."
        }
    ]

    for case in test_cases:
        print(f"{'='*70}")
        print(f"🚀 EJECUTANDO {case['id']}")
        print(f"📝 Propósito: {case['desc']}")
        print(f"📥 Input LP (Capital Call): '{case['query']}'")
        print(f"{'-'*70}")

        start_time = time.time()
        try:
            # Ejecución del motor RAG
            result = pipeline.resolve_entity(case["query"])
            elapsed_time = time.time() - start_time

            print(f"⏱️ Tiempo de resolución: {elapsed_time:.2f}s")
            print("📊 SALIDA ESTRUCTURADA (JSON):")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # --- VALIDACIÓN DE LA REGLA DE ORO DE NEGOCIO ---
            conf_score = result.get("confidence_score", 1.0)
            human_review = result.get("trigger_human_review")
            
            print(f"\n[Auditoría de Reglas]: Confidence Score = {conf_score}")
            if conf_score < 0.85 and human_review is True:
                print("✅ REGLA CUMPLIDA: Se detectó baja confianza y se forzó correctamente la revisión humana (trigger_human_review = true).")
            elif conf_score < 0.85 and human_review is False:
                print("❌ ALERTA DE ALUCINACIÓN: El score es menor a 0.85 pero NO se forzó la revisión humana.")
            elif conf_score >= 0.85 and human_review is False:
                print("✅ ALTA CONFIANZA: Resolución automática aprobada sin necesidad de intervención manual.")

        except Exception as e:
            print(f"\n❌ ERROR DURANTE LA EJECUCIÓN DEL PIPELINE: {str(e)}")
        
        print("\n")

if __name__ == "__main__":
    setup_database()
    run_evaluation_suite()