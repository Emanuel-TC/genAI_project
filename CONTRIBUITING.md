# Guía de Contribución y Reglas del Proyecto GenAI 🛠️

¡Bienvenidos al repositorio base del sistema Entity Resolution! 

Dado que trabajamos con una arquitectura de IA compleja (motores vectoriales locales, llamadas a APIs externas y flujos agénticos), necesitamos mantener el código blindado. Todos los contribuyentes deben seguir estas reglas **estrictas**:

## 1. Reglas de Git (Flujo de Trabajo)
* **NUNCA** trabajes directamente en `main` ni en `develop`.
* Para añadir un nuevo agente, test o capa de datos, crea una rama desde `develop`: `git checkout -b feature/nombre-de-tu-mejora`.
* Cuando tu código pase las pruebas de evaluación (`src/evaluation_suite.py`), sube tu rama y solicita una *Pull Request* (PR) para la integración.

## 2. Estructura de Directorios (Importante)
Mantén la limpieza arquitectónica. No guardes archivos fuera de su lugar:
* `data/`: Solo para archivos CSV de entrada (`Capital_Calls_DB.csv`).
* `vectorstore/`: Generado automáticamente por FAISS/BM25. **Nunca hagas commit** de los archivos dentro de esta carpeta (ya están en el `.gitignore`).
* `src/`: Lógica central (Pipelines, Indexadores, Agentes y Evaluadores).
* `notebooks/`: Exclusivamente para demos en `.ipynb` o análisis exploratorio.

## 3. Reglas de Código y Seguridad
* **Gestión de Secretos:** NUNCA subas claves de API (Tavily, Groq, OpenAI) al repositorio. Asegúrate de que el archivo `.env` permanece en el `.gitignore`.
* **Rutas Relativas:** Utiliza `src.config.Config` para el manejo de rutas (ej. `Config.CSV_PATH`). Están diseñadas con `pathlib` para ser multiplataforma (Linux, Windows, Mac).
* **Dependencias:** Si instalas una nueva librería de LangChain, Streamlit o Machine Learning en tu entorno virtual, es obligatorio actualizar el listado global ejecutando: `pip freeze > requirements.txt` (o añadiéndolo manualmente).

## 4. Pruebas y Validación (Testing de Agentes)
Antes de solicitar un *Merge*, debes demostrar que no has roto las reglas de negocio críticas del banco:
1. Asegúrate de que el entorno virtual está activo.
2. Ejecuta `python3 src/evaluation_suite.py`.
3. Para aprobar la PR, el **Safety Rate** no debe caer por debajo del **90%**. Si tu cambio en los *prompts* provoca que el LLM empiece a alucinar (falsos positivos entre distintas series de fondos), la PR será rechazada.

## 🔄 Resolución de Conflictos (Merge Conflicts)

A medida que varios ingenieros toquen los *prompts* o los esquemas de Pydantic, habrá conflictos. Sigue estos pasos para solucionarlos:

1. **Guarda tu trabajo:** `git add .` y `git commit -m "WIP"`
2. **Actualiza la rama principal:** `git fetch origin`
3. **Descarga novedades:** `git checkout develop` y `git pull origin develop`
4. **Fusiona en tu rama:** `git checkout tu-rama` y `git merge develop`
5. **Resuelve en el editor:** Abre tu VS Code, revisa las zonas resaltadas en rojo y acepta los cambios correctos.
6. **Informa la solución:** `git add .` y `git commit -m "Conflictos resueltos con develop"`