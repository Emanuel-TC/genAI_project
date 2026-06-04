# 🏦 Entity Resolution & Onboarding AI Agent

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Hybrid_RAG-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)
![Groq](https://img.shields.io/badge/LLM-Llama_3.3_70b-orange.svg)

Sistema Multiagente basado en Inteligencia Artificial Generativa y RAG Híbrido, diseñado para el sector de **Banca de Inversión**. Resuelve el problema crítico de *Entity Resolution* en las operaciones de *Capital Calls*, identificando inequívocamente a los *Limited Partners* (LPs) y orquestando el *Onboarding* de nuevas entidades mediante agentes de investigación web.

## 🎯 Propósito del Proyecto
Los bancos actúan como intermediarios en llamadas de capital, donde ingresan nombres de LPs con ruido sintáctico, omisiones legales o "falsos amigos" (ej. confundir el "Fund II" con el "Fund III"). Un algoritmo tradicional de similitud de texto genera falsos positivos críticos. 

Este proyecto utiliza **IA Generativa a temperatura 0.0** y reglas de negocio estrictas para razonar semánticamente, previniendo la financiación incorrecta de millones de dólares y automatizando el enriquecimiento de datos de entidades desconocidas.

## 🧠 Arquitectura del Sistema (5 Capas)
1. **Data Layer:** Preprocesamiento determinista (`LPNamePreprocessor`) para limpieza de sufijos legales y caracteres Unicode.
2. **Hybrid Retrieval Layer:** Fusión de búsqueda semántica (Embeddings densos `all-MiniLM-L6-v2` vía `FAISS`) y búsqueda léxica (`BM25Okapi`) mediante *Reciprocal Rank Fusion (RRF)*.
3. **Precision Layer:** Motor de compresión y reranking con `FlashRank` (*Cross-Encoder*) para maximizar la fidelidad del contexto.
4. **Agentic / LLM Layer:** Orquestador LangChain con modelos multi-proveedor (Groq/DeepSeek) evaluando umbrales de confianza (*Confidence Score*).
5. **UI/UX Layer:** Interfaz analítica interactiva desplegada en `Streamlit` para validación bajo el paradigma *Human-in-the-Loop*.

## 🤖 Estructura Multiagente
El flujo de decisión está controlado por tres agentes especializados:
* 🕵️‍♂️ **Matching Agent:** Compara la entidad entrante contra la base de datos corporativa. Filtra el ruido y penaliza diferencias críticas. Si el `confidence_score < 0.85`, fuerza la revisión humana.
* 🌐 **Research Agent (Tavily):** Si la entidad no existe, este agente navega por internet, lee webs financieras y estructura un borrador de alta (Sede, Tipo de Inversor, Ratings S&P/Moody's).
* 🛡️ **Validation Agent (UI):** Interfaz que orquesta el *Human-in-the-Loop*, permitiendo al analista revisar la evidencia y hacer persistir la nueva entidad en la BBDD, reentrenando la IA en tiempo real.

## 🚀 Instalación y Despliegue Local

### 1. Clonar y preparar entorno
```bash
git clone [https://github.com/Emanuel-TC/genAI_project](https://github.com/Emanuel-TC/genAI_project.git)
cd genAI_project
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Variables de Entorno
Crea un archivo .env en la raíz del proyecto y configura tus claves API:
```bash
GROQ_API_KEY=tu_clave_de_groq_aqui
TAVILY_API_KEY=tu_clave_de_tavily_aqui
# Opcional si decides usar OpenAI para embeddings:
# OPENAI_API_KEY=tu_clave_aqui
```

### 4. Ejecutar la Aplicación Web (Streamlit)
Despliega la interfaz de usuario interactiva:
```bash
streamlit run app.py
```
O si prefieres:
```bash
python3 -m streamlit run app.py
```

## 📊 Evaluación Cuantitativa y Pruebas
El proyecto incluye un script de evaluación nativo contra un Ground Truth Dataset de 15 casos extremos (Edge Cases).

Métricas alcanzadas:

- Hit Rate (Precisión de Match): 93.3%

- Safety Rate (Seguridad ante Falsos Positivos): 93.3%

Para ejecutar la batería de pruebas en consola y visualizar el Dashboard de Métricas:
```bash
python3 src/evaluation_suite.py
```

## 🤝 Contribuir
Si deseas colaborar en la mejora de este sistema agéntico, por favor revisa nuestro archivo [CONTRIBUITING.md](CONTRIBUITING.md) para conocer las políticas de ramas y estándares de desarrollo.