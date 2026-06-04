"""
MÓDULO DE FALLBACK MULTI-PROVEEDOR
Ubicación: src/fallback_factory.py
"""

from src.config import Config

class LLMFactory:
    
    @staticmethod
    def get_llm():
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
            
        elif provider == "deepseek":
            from langchain_openai import ChatOpenAI
            print(f"🔌 Inicializando LLM: DeepSeek ({Config.DEEPSEEK_MODEL})")
            # DeepSeek usa la misma arquitectura de API que OpenAI
            return ChatOpenAI(
                model=Config.DEEPSEEK_MODEL,
                temperature=temperature,
                api_key=Config.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com/v1"
            )
            
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")