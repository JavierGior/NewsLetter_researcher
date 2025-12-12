# main.py
import sys
import re  # <--- IMPORTANTE: Agregamos regex para filtrar URLs
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from config import EMPRESA, DIAS_BUSQUEDA, EMPRESAS_RELACIONADAS, TERMINOS_SECTOR
from utils.verificador import verificar_claves
from tools.buscador import tool_buscar_noticias
from utils.exportador_html import exportar_reporte

load_dotenv()

if not verificar_claves():
    sys.exit(1)

FECHA_HOY = datetime.now()
FECHA_INICIO = FECHA_HOY - timedelta(days=DIAS_BUSQUEDA)
RANGO_FECHAS_STR = f"Del {FECHA_INICIO.strftime('%d/%m/%Y')} al {FECHA_HOY.strftime('%d/%m/%Y')}"

class AgentState(TypedDict):
    raw_content: str
    social_content: str
    source_count: int
    final_report: str

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# --- NUEVA FUNCIÓN AUXILIAR PARA FILTRAR DUPLICADOS ---
def filtrar_y_acumular(texto_nuevo: str, urls_vistas: set) -> str:
    """
    Parsea el texto de salida del buscador, extrae las URLs y elimina
    los bloques ITEM completos si la URL ya fue vista en búsquedas anteriores.
    """
    if not texto_nuevo or "ITEM_" not in texto_nuevo:
        return texto_nuevo

    # Dividimos por bloques de items
    bloques = texto_nuevo.split("ITEM_")
    texto_limpio = []
    
    # Regex para encontrar la URL dentro del bloque formateado
    patron_url = re.compile(r"URL_REAL:\s*(.+)")

    for bloque in bloques:
        if not bloque.strip(): continue
        
        # Reconstruimos el string del bloque
        bloque_full = f"ITEM_{bloque}"
        
        # Buscamos la URL
        match = patron_url.search(bloque_full)
        if match:
            url = match.group(1).strip()
            # Si la URL ya la vimos en bloques anteriores, saltamos este item
            if url in urls_vistas:
                continue
            
            # Si es nueva, la guardamos en el set y agregamos el texto
            urls_vistas.add(url)
            texto_limpio.append(bloque_full)
        else:
            # Si por alguna razón no tiene URL, lo dejamos pasar por seguridad
            texto_limpio.append(bloque_full)
            
    return "".join(texto_limpio)

def investigador_node(state: AgentState):
    print(f"🕵️  Iniciando investigación (Motor: Google Serper): {RANGO_FECHAS_STR}")
    
    # Set de memoria para esta ejecución (evita duplicados entre bloques)
    urls_vistas_global = set()

    # 1. INTERNACIONAL
    print(f"   - Internacional...")
    raw_global = tool_buscar_noticias.invoke({
        "query": f"{EMPRESA} stock earnings agriculture finance", 
        "dias": DIAS_BUSQUEDA
    })
    # Filtramos inmediatamente
    res_global = filtrar_y_acumular(raw_global, urls_vistas_global)
    
    # 2. NACIONAL (Marca Principal)
    print(f"   - Nacional (Adecoagro)...")
    raw_nac_main = tool_buscar_noticias.invoke({
        "query": f'"{EMPRESA}" Argentina', 
        "dias": DIAS_BUSQUEDA
    })
    res_nac_main = filtrar_y_acumular(raw_nac_main, urls_vistas_global)
    
    # 3. NACIONAL (Subsidiarias)
    print(f"   - Subsidiarias...")
    subs_clean = " OR ".join([f'"{e}"' for e in EMPRESAS_RELACIONADAS[:4]])
    raw_nac_sub = tool_buscar_noticias.invoke({
        "query": f"({subs_clean}) Argentina", 
        "dias": DIAS_BUSQUEDA
    })
    res_nac_sub = filtrar_y_acumular(raw_nac_sub, urls_vistas_global)

    # 4. SECTOR Y COMPETENCIA
    print(f"   - Sector y Competencia...")
    query_sector = " OR ".join(TERMINOS_SECTOR)
    raw_sector = tool_buscar_noticias.invoke({
        "query": f"({query_sector}) Argentina",
        "dias": DIAS_BUSQUEDA
    })
    # Aquí es donde más duplicados suelen aparecer, el filtro los eliminará
    res_sector = filtrar_y_acumular(raw_sector, urls_vistas_global)
    
    # 5. REDES SOCIALES
    print(f"   - Redes Sociales...")
    res_social = tool_buscar_noticias.invoke({
        "query": f'"{EMPRESA}" (site:twitter.com OR site:facebook.com OR site:instagram.com OR site:linkedin.com OR site:youtube.com)', 
        "dias": DIAS_BUSQUEDA
    })
    
    full_text = (
        f"=== BLOQUE INTERNACIONAL ===\n{res_global}\n\n"
        f"=== BLOQUE NACIONAL (MARCA) ===\n{res_nac_main}\n\n"
        f"=== BLOQUE NACIONAL (SUBSIDIARIAS) ===\n{res_nac_sub}\n\n"
        f"=== BLOQUE SECTOR/COMPETENCIA ===\n{res_sector}"
    )
    
    # Contamos URLs únicas reales encontradas
    count = len(urls_vistas_global)
    return {"raw_content": full_text, "social_content": res_social, "source_count": count}

def redactor_node(state: AgentState):
    print("✍️  Redactor generando reporte con formato visual...")
    
    news_data = state["raw_content"]
    social_data = state["social_content"]
    count = state["source_count"]
    
    # Prompt optimizado para DEDUPLICACIÓN SEMÁNTICA
    prompt = f"""
    Eres un analista de inteligencia corporativa experto. Genera el reporte para {EMPRESA}.
    
    RANGO DE FECHAS VÁLIDO: {RANGO_FECHAS_STR}
    
    INPUT NOTICIAS:
    {news_data}
    
    INPUT SOCIAL:
    {social_data}
    
    INSTRUCCIONES OBLIGATORIAS:
    1. **NO INVENTAR LINKS:** Usa solo los `URL_REAL` provistos.
    2. **DEDUPLICACIÓN SEMÁNTICA (CRÍTICO):** 
       - Si encuentras múltiples noticias cubriendo el **MISMO HECHO** (aunque sean de fuentes distintas como Clarín y La Nación), **AGRÚPALAS** en un solo ítem.
       - Usa el título más descriptivo.
       - Al final de la línea pon: [Leer más en Fuente 1](url1) | [Fuente 2](url2).
       - NO generes dos ítems separados para la misma historia.
    3. **CLASIFICACIÓN:**
       - Noticias de Adecoagro/Subsidiarias van primero.
       - Noticias generales del sector (Sancor, clima) van en su sección, salvo que mencionen explícitamente a Adecoagro.
    4. **SENTIMIENTO VISUAL:** Usa ÚNICAMENTE: 🙂, 😐, 😠.
    
    ESTRUCTURA DE SALIDA (Markdown estricto):
    
    # Reporte de Sentimiento - {EMPRESA}
    **Período:** {RANGO_FECHAS_STR} | **Fuentes Únicas:** {count}
    
    ## 📈 Análisis General
    [Resumen ejecutivo de 1 párrafo sobre la situación de la empresa y el sector]
    
    ## 📊 Reporte de Sentimiento
    
    ### Datos Sentimiento
    * Positivo: [Número]
    * Neutro: [Número]
    * Negativo: [Número]
    
    ### Datos Volumen por Marca
    * Menciones Adecoagro: [Número]
    * Menciones Pilagá: [Número]
    * Menciones Molinos Ala: [Número]
    * Menciones La Lácteo: [Número]
    
    ## 🇦🇷 Panorama Nacional
    [Análisis coyuntura local]
    
    ## 🌍 Panorama Internacional
    [Análisis mercado global/acciones]
    
    ## 💬 Resumen Conversación Digital
    
 ### Data Social
    * Total Menciones: [Suma]
    [LISTA DINÁMICA: SOLO REDES CON MENCIONES > 0. NO PONGAS LAS QUE TIENEN 0]
    * [Nombre Red]: [N]
    * [Nombre Red]: [N]
    ...
    * Social Positivo: [N]
    * Social Neutro: [N]
    * Social Negativo: [N]
    
    [Breve análisis redes]
    
    ## 📰 Detalle de Noticias
    
    ### 🇦🇷 Adecoagro y Subsidiarias
    [Lista noticias directas agrupadas por tema. Si no hay: "Sin novedades directas".
    Formato:
    [EMOJI] **Título** - [Leer Fuente 1](URL1) | [Leer Fuente 2](URL2)
    > *"Extracto..."*
    ]
    
    ### 🚜 Novedades del Sector (Competencia y Contexto)
    [Lista noticias sectoriales. Agrupa si hay temas repetidos.
    Formato:
    [EMOJI] **Título** - [Leer más](URL_REAL)
    > *"Extracto..."*
    ]

    ### 🌐 Internacional
    [Lista noticias internacionales.
    Formato:
    [EMOJI] **Título** - [Leer más](URL_REAL)
    > *"Extracto..."*
    ]
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_report": response.content}

workflow = StateGraph(AgentState)
workflow.add_node("investigador", investigador_node)
workflow.add_node("redactor", redactor_node)

workflow.set_entry_point("investigador")
workflow.add_edge("investigador", "redactor")
workflow.add_edge("redactor", END)

app = workflow.compile()

if __name__ == "__main__":
    print(f"🚀 Sistema v10.1 (Anti-Duplicados | Fecha: {RANGO_FECHAS_STR})")
    try:
        res = app.invoke({
            "raw_content": "", 
            "social_content": "", 
            "source_count": 0, 
            "final_report": ""
        })
        exportar_reporte(res["final_report"], EMPRESA)
    except Exception as e:
        print(f"❌ Error en la ejecución: {e}")
        import traceback
        traceback.print_exc()