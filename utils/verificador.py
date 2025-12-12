# utils/verificador.py
import os
from dotenv import load_dotenv

def verificar_claves():
    print("🔑 VERIFICACIÓN DE API KEYS")
    print("=" * 60)
    
    load_dotenv()
    # tavily_key = os.getenv("TAVILY_API_KEY") # Ya no es estrictamente necesaria si usamos Serper
    openai_key = os.getenv("OPENAI_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY") # <--- NUEVA
    
    if not serper_key:
        print("❌ SERPER_API_KEY no encontrada en .env (Necesaria para Google Search)")
        return False
    
    if not openai_key:
        print("❌ OPENAI_API_KEY no encontrada en .env")
        return False
    
    print(f"✅ SERPER_API_KEY: {serper_key[:10]}... configurada")
    print(f"✅ OPENAI_API_KEY: {openai_key[:15]}... configurada")
    return True