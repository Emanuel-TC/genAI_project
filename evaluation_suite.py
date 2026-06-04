"""
MÓDULO DE EVALUACIÓN CUANTITATIVA
Ubicación: src/evaluation_suite.py

Ejecuta una batería de pruebas automatizada sobre un conjunto de datos etiquetado 
(Ground Truth) para calcular el Hit Rate (Tasa de Acierto) y la Precisión del 
Umbral de Seguridad (Confidence Score Threshold) del sistema multiagente.
"""

import time
import json
from typing import List, Dict
from src.rag_pipeline import EntityResolutionPipeline

class RAGEvaluator:
    def __init__(self):
        print("🔌 Inicializando motor de evaluación RAG...")
        self.pipeline = EntityResolutionPipeline()
        
        # GROUND TRUTH DATASET (15 Casos Representativos)
        self.dataset = [
            # CATEGORÍA 1: Match Positivo (Ruido Sintáctico o Tipográfico)
            {"query": "ANTARIUS S.A.", "exp_match": True, "exp_review": False, "cat": "Ruido Leve"},
            {"query": "Al Sariya Commercial Investments L.L.C.", "exp_match": True, "exp_review": False, "cat": "Ruido Leve"},
            {"query": "Alecta pensionsforsakring, omsesidigt", "exp_match": True, "exp_review": False, "cat": "Falta Diéresis"},
            {"query": "BNP Paribas", "exp_match": True, "exp_review": False, "cat": "Match Exacto"},
            {"query": "DHFI 13 FZ LLC", "exp_match": True, "exp_review": False, "cat": "Ruido Leve"},
            
            # CATEGORÍA 2: Falsos Amigos (Misma familia, distinto fondo/serie) -> Riesgo Crítico
            {"query": "Appia IV Global Infrastructure Portfolio SCSp", "exp_match": False, "exp_review": True, "cat": "Serie Distinta (IV vs III)"},
            {"query": "Border to Coast Bedfordshire Fund II LP", "exp_match": False, "exp_review": True, "cat": "Serie Distinta (Fund II)"},
            {"query": "Caisse Regionale Crédit Agricole Mutuel de Paris", "exp_match": False, "exp_review": True, "cat": "Geografía Distinta (Paris)"},
            {"query": "Border to Coast London LP", "exp_match": False, "exp_review": True, "cat": "Geografía Distinta (London)"},
            {"query": "DHFI 14 FZ-LLC", "exp_match": False, "exp_review": True, "cat": "Serie Distinta (14 vs 13)"},
            
            # CATEGORÍA 3: Entidades Inexistentes
            {"query": "Tech Ventures Capital Innovacion SA", "exp_match": False, "exp_review": True, "cat": "Inexistente"},
            {"query": "Global Horizon Partners L.P.", "exp_match": False, "exp_review": True, "cat": "Inexistente"},
            {"query": "Banco Santander Investment Hub", "exp_match": False, "exp_review": True, "cat": "Inexistente"},
            {"query": "NextGen Renewable Energy Fund", "exp_match": False, "exp_review": True, "cat": "Inexistente"},
            {"query": "Omega Quantitative Solutions LLC", "exp_match": False, "exp_review": True, "cat": "Inexistente"}
        ]

    def run_evaluation(self):
        print(f"\n🚀 Iniciando Evaluación sobre {len(self.dataset)} casos de prueba...")
        print("="*80)
        
        match_correctos = 0
        seguridad_correcta = 0
        tiempos_resolucion = []
        
        for i, case in enumerate(self.dataset, 1):
            query = case["query"]
            exp_match = case["exp_match"]
            exp_review = case["exp_review"]
            categoria = case["cat"]
            
            print(f"[{i}/{len(self.dataset)}] Testeando ({categoria}): '{query}'")
            
            start_time = time.time()
            try:
                # Evitar mostrar todos los prints internos del pipeline para limpiar la consola
                result = self.pipeline.chain.invoke(query)
                elapsed = time.time() - start_time
                tiempos_resolucion.append(elapsed)
                
                # Obtener predicciones
                pred_match = result.get("is_match", False)
                pred_review = result.get("trigger_human_review", True)
                
                # Calcular aciertos
                is_match_correct = (pred_match == exp_match)
                is_safety_correct = (pred_review == exp_review)
                
                if is_match_correct: match_correctos += 1
                if is_safety_correct: seguridad_correcta += 1
                
                # Feedback visual en consola
                status = "✅ PASS" if (is_match_correct and is_safety_correct) else "❌ FAIL"
                print(f"   ↳ {status} | Match Esperado: {exp_match}(Pred: {pred_match}) | Revisión Esperada: {exp_review}(Pred: {pred_review}) | Score: {result.get('confidence_score', 0):.2f}")
                
            except Exception as e:
                print(f"   ↳ ⚠️ ERROR en ejecución: {str(e)}")
        
        self._print_dashboard(match_correctos, seguridad_correcta, tiempos_resolucion)

    def _print_dashboard(self, match_correctos: int, seguridad_correcta: int, tiempos: List[float]):
        total = len(self.dataset)
        hit_rate = (match_correctos / total) * 100
        safety_rate = (seguridad_correcta / total) * 100
        avg_time = sum(tiempos) / len(tiempos) if tiempos else 0
        
        print("\n" + "="*80)
        print(" 📊 DASHBOARD DE MÉTRICAS - ENTITY RESOLUTION PIPELINE")
        print("="*80)
        print(f" 📈 Hit Rate (Precisión de Match):        {hit_rate:.1f}% ({match_correctos}/{total})")
        print(f" 🛡️ Safety Rate (Precisión de Seguridad):  {safety_rate:.1f}% ({seguridad_correcta}/{total})")
        print(f" ⏱️ Latencia Media por Query:              {avg_time:.2f} segundos")
        print("="*80)
        print("\n💡 CONCLUSIÓN PARA EL TRIBUNAL:")
        if safety_rate > 90:
            print("El sistema es altamente seguro para banca de inversión. Las reglas estrictas")
            print("previenen alucinaciones y derivan los 'Edge Cases' a revisión manual exitosamente.")
        else:
            print("Se requiere ajustar el CONFIDENCE_THRESHOLD o revisar las instrucciones del LLM.")
        print("="*80 + "\n")

if __name__ == "__main__":
    evaluator = RAGEvaluator()
    evaluator.run_evaluation()