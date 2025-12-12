# utils/exportador_html.py
import os
import webbrowser
from datetime import datetime
from config import COLOR_PRINCIPAL, COLOR_SECUNDARIO, COLOR_TEXTO, COLOR_FONDO

def exportar_reporte(contenido_markdown: str, empresa: str):
    """
    Exporta el reporte a múltiples formatos: TXT, HTML y abre el navegador.
    """
    fecha_hoy = datetime.now().strftime("%Y%m%d_%H%M%S")
    fecha_formateada = datetime.now().strftime('%d/%m/%Y')
    
    # Nombres de archivos
    nombre_txt = f"reporte_{empresa.lower()}_{fecha_hoy}.txt"
    nombre_html = f"reporte_{empresa.lower()}_{fecha_hoy}.html"
    
    # 1. Guardar archivo TXT
    try:
        with open(nombre_txt, "w", encoding="utf-8") as f:
            f.write(contenido_markdown)
        print(f"✅ Reporte TXT guardado: {nombre_txt}")
    except Exception as e:
        print(f"⚠️  No se pudo guardar el archivo TXT: {e}")
        return False
    
    # 2. Generar y guardar archivo HTML
    try:
        html_content = generar_html_desde_markdown(contenido_markdown, fecha_formateada)
        with open(nombre_html, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✅ Reporte HTML guardado: {nombre_html}")
    except Exception as e:
        print(f"⚠️  No se pudo guardar el archivo HTML: {e}")
        return False
    
    # 3. Abrir en navegador
    try:
        ruta_absoluta = os.path.abspath(nombre_html)
        webbrowser.open(f"file://{ruta_absoluta}")
        print(f"🌐 Abriendo reporte en navegador...")
        return True
    except Exception as e:
        print(f"⚠️  No se pudo abrir el navegador automáticamente: {e}")
        print(f"   Puedes abrir manualmente: {os.path.abspath(nombre_html)}")
        return False

def generar_html_desde_markdown(contenido_markdown: str, fecha_reporte: str) -> str:
    """
    Convierte el contenido Markdown a HTML con estilos de Adecoagro
    y formato visual mejorado.
    """
    
    import re
    
    # Procesar el contenido Markdown
    contenido_html = contenido_markdown
    
    # Convertir encabezados
    contenido_html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', contenido_html, flags=re.MULTILINE)
    contenido_html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', contenido_html, flags=re.MULTILINE)
    contenido_html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', contenido_html, flags=re.MULTILINE)
    
    # Convertir listas
    contenido_html = re.sub(r'^- (.+)$', r'<li>• \1</li>', contenido_html, flags=re.MULTILINE)
    contenido_html = re.sub(r'(<li>.*</li>)', r'<ul class="menciones-lista">\1</ul>', contenido_html, flags=re.DOTALL)
    
    # Convertir listas numeradas
    contenido_html = re.sub(r'^(\d+)\. (.+)$', r'<li><strong>\1.</strong> \2</li>', contenido_html, flags=re.MULTILINE)
    
    # Convertir URLs
    url_regex = r'(https?:\/\/[^\s\n]+)'
    contenido_html = re.sub(url_regex, r'<a href="\1" target="_blank">\1</a>', contenido_html)
    
    # Convertir negritas
    contenido_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', contenido_html)
    
    # Reemplazar saltos de línea
    contenido_html = contenido_html.replace('\n', '<br>')
    
    # Plantilla HTML
    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Sentimiento - Adecoagro</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Open+Sans:wght@400;600&display=swap');
        
        body {{
            font-family: 'Open Sans', sans-serif;
            line-height: 1.6;
            color: {COLOR_TEXTO};
            background: linear-gradient(135deg, #f9f9f9 0%, #eef2e6 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
            border: 1px solid rgba(46, 125, 50, 0.1);
        }}
        
        h1 {{
            font-family: 'Montserrat', sans-serif;
            color: {COLOR_PRINCIPAL};
            border-bottom: 4px solid {COLOR_SECUNDARIO};
            padding-bottom: 15px;
            margin-bottom: 25px;
            font-size: 2.2em;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        
        .periodo {{
            background: linear-gradient(to right, {COLOR_PRINCIPAL}, #1B5E20);
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
            display: inline-block;
            font-weight: 600;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        h2 {{
            font-family: 'Montserrat', sans-serif;
            color: {COLOR_PRINCIPAL};
            margin-top: 30px;
            padding: 10px 0;
            border-bottom: 2px solid {COLOR_SECUNDARIO};
            font-weight: 600;
        }}
        
        .menciones-lista {{
            list-style: none;
            padding: 0;
            margin: 20px 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .menciones-lista li {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 5px solid {COLOR_SECUNDARIO};
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }}
        
        .menciones-lista li:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .positivo {{ color: #2E7D32; }}
        .neutro {{ color: #F57C00; }}
        .negativo {{ color: #C62828; }}
        
        .resumen-general {{
            background: linear-gradient(to right, rgba(255, 213, 79, 0.1), rgba(255, 213, 79, 0.05));
            padding: 25px;
            border-radius: 10px;
            margin: 25px 0;
            border-left: 5px solid {COLOR_SECUNDARIO};
            font-size: 1.05em;
            line-height: 1.7;
        }}
        
        h3 {{
            font-family: 'Montserrat', sans-serif;
            color: {COLOR_PRINCIPAL};
            margin-top: 30px;
            font-weight: 600;
            position: relative;
            padding-left: 30px;
        }}
        
        h3::before {{
            content: "▸";
            position: absolute;
            left: 0;
            color: {COLOR_SECUNDARIO};
            font-size: 1.5em;
            line-height: 1;
        }}
        
        ul {{
            list-style: none;
            padding: 0;
        }}
        
        li {{
            margin: 18px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
            border-left: 3px solid {COLOR_SECUNDARIO};
        }}
        
        li:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-left: 3px solid {COLOR_PRINCIPAL};
        }}
        
        a {{
            color: {COLOR_PRINCIPAL};
            text-decoration: none;
            font-weight: 600;
            display: block;
            margin-top: 8px;
            padding: 5px 10px;
            background: rgba(46, 125, 50, 0.05);
            border-radius: 4px;
            transition: all 0.2s ease;
            word-break: break-all;
        }}
        
        a:hover {{
            background: {COLOR_PRINCIPAL};
            color: white;
            text-decoration: none;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .emoji {{
            font-size: 3em;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="emoji">🌾</div>
            <h1>Reporte de Sentimiento - Adecoagro</h1>
            <div class="periodo">**Período:** {fecha_reporte}</div>
        </div>
        
        <div id="content">
            {contenido_html}
        </div>
        
        <div class="footer">
            <p>Reporte generado automáticamente | Inteligencia de Mercados</p>
        </div>
    </div>
</body>
</html>
"""
    return html_template