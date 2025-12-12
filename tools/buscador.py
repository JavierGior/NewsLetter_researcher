# tools/buscador.py
import requests
import json
import os
from langchain_core.tools import tool
from config import MAX_NOTICIAS

@tool
def tool_buscar_noticias(query: str, dias: int = 2) -> str:
    """
    Busca en Google usando Serper.dev con filtro de tiempo nativo.
    NO filtra en Python para evitar falsos negativos.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "ERROR CRÍTICO: Falta SERPER_API_KEY en .env"

    # Limpieza de query para Google (quitamos operadores complejos que a veces rompen la API)
    # Dejamos lo básico.
    print(f"   🔎 Googleando (Serper): '{query[:60]}...' [Últimos {dias} días]")
    
    url = "https://google.serper.dev/search"
    
    # Parametro de tiempo de Google: qdr:d (días) o qdr:h (horas)
    # Si dias=1 (ayer), pedimos 24h (d1). Si dias=2, pedimos d2.
    tbs_param = f"qdr:d{dias}"
    
    payload = json.dumps({
        "q": query,
        "gl": "ar",      # Geolocalización Argentina
        "hl": "es",      # Idioma Español
        "num": 20,       # Pedimos 20 por bloque
        "tbs": tbs_param # FILTRO DE TIEMPO DEL MOTOR
    })
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        
        # Recopilar resultados de Noticias y Orgánicos
        resultados = []
        
        # 1. Bloque "news" (Si aparece)
        if "news" in data:
            resultados.extend(data["news"])
            
        # 2. Bloque "organic" (Web normal)
        if "organic" in data:
            resultados.extend(data["organic"])
            
        if not resultados:
            # DEBUG: Si sale 0, imprimimos qué pasó
            print(f"      ⚠️  Google devolvió 0 resultados. Respuesta cruda: {str(data)[:200]}...")
            return "Google no encontró noticias recientes."

        formatted_output = ""
        contador = 0
        links_vistos = set()
        
        print(f"      ✅ Google trajo {len(resultados)} candidatos raw...")

        for r in resultados:
            if contador >= MAX_NOTICIAS: break
            
            link = r.get('link')
            if not link or link in links_vistos: continue
            
            title = r.get('title', 'Sin título')
            snippet = r.get('snippet', '')
            date_str = r.get('date', 'Fecha no provista por API')
            source = r.get('source', 'Web')
            
            # FILTRO: Solo descartamos si es explícitamente YouTube (opcional, ya que lo pides en social)
            # Pero para noticias generales, dejamos pasar todo lo que Google mandó.
            
            links_vistos.add(link)
            
            formatted_output += f"ITEM_{contador + 1}\n"
            formatted_output += f"FECHA_GOOGLE: {date_str}\n"
            formatted_output += f"FUENTE: {source}\n"
            formatted_output += f"TITULO: {title}\n"
            formatted_output += f"URL_REAL: {link}\n"
            formatted_output += f"RESUMEN: {snippet}\n"
            formatted_output += "-" * 40 + "\n"
            
            contador += 1
            
        return formatted_output

    except Exception as e:
        return f"Error Serper: {e}"