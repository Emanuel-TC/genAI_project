"""
MÓDULO DE FALLBACK MULTI-PROVEEDOR
Ubicación: src/fallback_factory.py

Implementa un patrón Factory para conmutar dinámicamente entre OpenAI, 
Groq y Google Gemini sin necesidad de alterar el pipeline principal.
"""

from src.config import Config

class LLMFactory:
    """
    Fábrica encargada de instanciar el modelo de lenguaje de acuerdo
    a la configuración centralizada, forzando parámetros de producción
    como la temperatura a 0.0 para procesos deterministas.
    """
    
    @staticmethod
    def get_llm():
        # Validar credenciales antes de intentar la instanciación
        Config.validate_config()
        
        provider = Config.LLM_PROVIDER
        temperature = Config.LLM_TEMPERATURE
        
        if provider == "openai":
            from langchain_openai import ChatOpenAI
            print(f"🔌 Inicializando LLM: OpenAI ({Config.OPENAI_MODEL})")
            return ChatOpenAI(
                model=Config.OPENAI_MODEL,
                temperature=temperature,
                api_key=Config.OPENAI_API_KEY
            )
            
        elif provider == "groq":
            from langchain_groq import ChatGroq
            print(f"🔌 Inicializando LLM: Groq ({Config.GROQ_MODEL})")
            return ChatGroq(
                model=Config.GROQ_MODEL,
                temperature=temperature,
                api_key=Config.GROQ_API_KEY
            )
            
        elif provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            print(f"🔌 Inicializando LLM: Google Gemini ({Config.GOOGLE_MODEL})")
            return ChatGoogleGenerativeAI(
                model=Config.GOOGLE_MODEL,
                temperature=temperature,
                api_key=Config.GOOGLE_API_KEY
            )
            
        else:
            # Por robustez, aunque ya validamos en config.py, manejamos el fallback final
            raise ValueError(f"Proveedor no soportado: {provider}")