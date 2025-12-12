import sys
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

# Asegúrate de importar EMPRESAS_RELACIONADAS aquí
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

def filtrar_y_acumular(texto_nuevo: str, urls_vistas: set) -> str:
    if not texto_nuevo or "ITEM_" not in texto_nuevo:
        return texto_nuevo
    bloques = texto_nuevo.split("ITEM_")
    texto_limpio = []
    patron_url = re.compile(r"URL_REAL:\s*(.+)")

    for bloque in bloques:
        if not bloque.strip(): continue
        bloque_full = f"ITEM_{bloque}"
        match = patron_url.search(bloque_full)
        if match:
            url = match.group(1).strip()
            if url in urls_vistas:
                continue
            urls_vistas.add(url)
            texto_limpio.append(bloque_full)
        else:
            texto_limpio.append(bloque_full)
    return "".join(texto_limpio)

def investigador_node(state: AgentState):
    print(f"🕵️  Iniciando investigación para {EMPRESA}: {RANGO_FECHAS_STR}")
    
    urls_vistas_global = set()

    # 1. INTERNACIONAL
    print(f"   - Internacional...")
    raw_global = tool_buscar_noticias.invoke({
        "query": f"{EMPRESA} stock earnings agriculture finance", 
        "dias": DIAS_BUSQUEDA
    })
    res_global = filtrar_y_acumular(raw_global, urls_vistas_global)
    
    # 2. NACIONAL (Marca Principal)
    # MODIFICADO: Usa la variable EMPRESA
    print(f"   - Nacional ({EMPRESA})...")
    raw_nac_main = tool_buscar_noticias.invoke({
        "query": f'"{EMPRESA}" Argentina', 
        "dias": DIAS_BUSQUEDA
    })
    res_nac_main = filtrar_y_acumular(raw_nac_main, urls_vistas_global)
    
    # 3. NACIONAL (Subsidiarias)
    print(f"   - Subsidiarias...")
    # MODIFICADO: Usa la lista importada dinámicamente
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
    res_sector = filtrar_y_acumular(raw_sector, urls_vistas_global)
    
    # 5. REDES SOCIALES
    print(f"   - Redes Sociales...")
    res_social = tool_buscar_noticias.invoke({
        "query": f'"{EMPRESA}" (site:twitter.com OR site:facebook.com OR site:instagram.com OR site:linkedin.com OR site:youtube.com)', 
        "dias": DIAS_BUSQUEDA
    })
    
    full_text = (
        f"=== BLOQUE INTERNACIONAL ===\n{res_global}\n\n"
        f"=== BLOQUE NACIONAL (MARCA PRINCIPAL) ===\n{res_nac_main}\n\n"
        f"=== BLOQUE NACIONAL (SUBSIDIARIAS) ===\n{res_nac_sub}\n\n"
        f"=== BLOQUE SECTOR/COMPETENCIA ===\n{res_sector}"
    )
    
    count = len(urls_vistas_global)
    return {"raw_content": full_text, "social_content": res_social, "source_count": count}

def redactor_node(state: AgentState):
    print("✍️  Redactor generando reporte con formato visual...")
    
    news_data = state["raw_content"]
    social_data = state["social_content"]
    count = state["source_count"]
    
    # --- CONSTRUCCIÓN DINÁMICA DEL PROMPT ---
    # Creamos la lista de subsidiarias formateada para que el LLM sepa qué buscar
    # Ejemplo resultado: "* Menciones Pilagá: [Número]\n    * Menciones Molinos Ala: [Número]"
    lista_subsidiarias_prompt = "\n    ".join([f"* Menciones {sub}: [Número]" for sub in EMPRESAS_RELACIONADAS])
    
    prompt = f"""
    Eres un analista de inteligencia corporativa experto. Genera el reporte para la empresa: {EMPRESA}.
    
    RANGO DE FECHAS VÁLIDO: {RANGO_FECHAS_STR}
    
    INPUT NOTICIAS:
    {news_data}
    
    INPUT SOCIAL:
    {social_data}
    
    INSTRUCCIONES OBLIGATORIAS:
    1. **NO INVENTAR LINKS:** Usa solo los `URL_REAL` provistos.
    2. **DEDUPLICACIÓN SEMÁNTICA (CRÍTICO):** 
       - Si encuentras múltiples noticias cubriendo el **MISMO HECHO**, AGRÚPALAS.
       - Usa el título más descriptivo.
    3. **CLASIFICACIÓN:**
       - Noticias de **{EMPRESA}** y sus marcas relacionadas ({', '.join(EMPRESAS_RELACIONADAS)}) van primero.
       - Noticias generales del sector van en su sección, salvo que mencionen explícitamente a {EMPRESA}.
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
    * Menciones {EMPRESA}: [Número]
    {lista_subsidiarias_prompt}
    
    ## 🇦🇷 Panorama Nacional
    [Análisis coyuntura local]
    
    ## 🌍 Panorama Internacional
    [Análisis mercado global/acciones]
    
    ## 💬 Resumen Conversación Digital
    
 ### Data Social
    * Total Menciones: [Suma]
    [LISTA DINÁMICA: SOLO REDES CON MENCIONES > 0]
    * [Nombre Red]: [N]
    ...
    * Social Positivo: [N]
    * Social Neutro: [N]
    * Social Negativo: [N]
    
    [Breve análisis redes]
    
    ## 📰 Detalle de Noticias
    
    ### 🇦🇷 {EMPRESA} y Subsidiarias
    [Lista noticias directas agrupadas por tema. Si no hay: "Sin novedades directas".]
    
    ### 🚜 Novedades del Sector (Competencia y Contexto)
    [Lista noticias sectoriales.]

    ### 🌐 Internacional
    [Lista noticias internacionales.]
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
    print(f"🚀 Sistema v10.2 (Agnóstico | Fecha: {RANGO_FECHAS_STR})")
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
