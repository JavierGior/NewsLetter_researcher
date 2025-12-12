# utils/exportador_html.py
import os
import re
import webbrowser
import markdown
from datetime import datetime
from config import COLOR_PRINCIPAL, COLOR_SECUNDARIO

def extract_metrics(md_text):
    def get_val(pattern, text):
        match = re.search(pattern, text, re.IGNORECASE)
        return int(match.group(1)) if match else 0

    return {
        "gen": [
            get_val(r'\*\s*Positivo:\s*(\d+)', md_text),
            get_val(r'\*\s*Neutro:\s*(\d+)', md_text),
            get_val(r'\*\s*Negativo:\s*(\d+)', md_text)
        ],
        "brands": [
            get_val(r'\*\s*Menciones Adecoagro:\s*(\d+)', md_text),
            get_val(r'\*\s*Menciones Pilagá:\s*(\d+)', md_text),
            get_val(r'\*\s*Menciones Molinos Ala:\s*(\d+)', md_text),
            get_val(r'\*\s*Menciones La Lácteo:\s*(\d+)', md_text)
        ],
        "soc_vol": [
            get_val(r'\*\s*Facebook:\s*(\d+)', md_text),
            get_val(r'\*\s*Instagram:\s*(\d+)', md_text),
            get_val(r'\*\s*X \(Twitter\):\s*(\d+)', md_text),
            get_val(r'\*\s*TikTok:\s*(\d+)', md_text),
            get_val(r'\*\s*YouTube:\s*(\d+)', md_text)
        ],
        "soc_sent": [
            get_val(r'\*\s*Social Positivo:\s*(\d+)', md_text),
            get_val(r'\*\s*Social Neutro:\s*(\d+)', md_text),
            get_val(r'\*\s*Social Negativo:\s*(\d+)', md_text)
        ]
    }

def exportar_reporte(contenido_markdown: str, empresa: str):
    metrics = extract_metrics(contenido_markdown)
    
    html_content = markdown.markdown(contenido_markdown, extensions=['extra', 'nl2br'])
    flag_img = '<img src="https://flagcdn.com/h24/ar.png" alt="AR" style="vertical-align:text-bottom; height:20px;">'
    html_content = html_content.replace("🇦🇷", flag_img)
    html_content = re.sub(r'<a href="(http[^"]+)"', r'<a href="\1" target="_blank"', html_content)

    headers_map = {
        '<h2>📈 Análisis General</h2>': 'analisis-general',
        '<h2>📊 Reporte de Sentimiento</h2>': 'reporte-sentimiento',
        f'<h2>{flag_img} Panorama Nacional</h2>': 'panorama-nacional',
        '<h2>🌍 Panorama Internacional</h2>': 'panorama-internacional',
        '<h2>💬 Resumen Conversación Digital</h2>': 'resumen-digital',
        '<h2>📰 Detalle de Noticias</h2>': 'detalle-noticias'
    }
    for tag, uid in headers_map.items():
        html_content = html_content.replace(tag, f'<h2 id="{uid}">{tag[4:-5]}</h2>')

    charts_gen_html = """
    <div class="dashboard-row">
        <div class="chart-card">
            <h4>Distribución de Sentimiento</h4>
            <div class="chart-container"><canvas id="chartGenSent"></canvas></div>
        </div>
        <div class="chart-card">
            <h4>Volumen por Marca</h4>
            <div class="chart-container"><canvas id="chartBrandVol"></canvas></div>
        </div>
    </div>
    """
    html_content = html_content.replace('id="reporte-sentimiento">📊 Reporte de Sentimiento</h2>', 
                                      'id="reporte-sentimiento">📊 Reporte de Sentimiento</h2>' + charts_gen_html)

    charts_soc_html = """
    <div class="dashboard-row">
        <div class="chart-card">
            <h4>Volumen por Red (Treemap)</h4>
            <div class="chart-container"><canvas id="chartSocTree"></canvas></div>
        </div>
        <div class="chart-card">
            <h4>Sentimiento Social</h4>
            <div class="chart-container"><canvas id="chartSocSent"></canvas></div>
        </div>
    </div>
    """
    html_content = html_content.replace('id="resumen-digital">💬 Resumen Conversación Digital</h2>', 
                                      'id="resumen-digital">💬 Resumen Conversación Digital</h2>' + charts_soc_html)

    # CSS REVERTIDO A ESTILO LIMPIO (SIN BORDES VERDES)
    css = f"""
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        body {{ font-family: 'Roboto', sans-serif; background: #f0f2f5; color: #333; margin: 0; padding: 20px; }}
        .container {{ max-width: 950px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); padding: 40px; }}
        .header {{ text-align: center; margin-bottom: 25px; }}
        h1 {{ color: {COLOR_PRINCIPAL}; margin: 0; font-size: 2.2em; }}
        .periodo {{ color: #777; font-size: 0.9em; }}
        .nav-bar {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-bottom: 40px; background: #fafafa; padding: 15px; border-radius: 8px; }}
        .nav-btn {{ background: white; color: {COLOR_PRINCIPAL}; border: 1px solid #ddd; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 0.85em; font-weight: 600; transition: all 0.2s; }}
        .nav-btn:hover {{ background: {COLOR_PRINCIPAL}; color: white; border-color: {COLOR_PRINCIPAL}; }}
        h2 {{ color: {COLOR_PRINCIPAL}; border-bottom: 2px solid {COLOR_SECUNDARIO}; padding-bottom: 10px; margin-top: 50px; font-size: 1.5em; }}
        .dashboard-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 25px 0; }}
        .chart-card {{ background: #fff; border: 1px solid #eee; border-radius: 10px; padding: 15px; text-align: center; }}
        .chart-card h4 {{ margin: 0 0 10px 0; color: #555; font-size: 0.85em; text-transform: uppercase; }}
        .chart-container {{ position: relative; height: 200px; width: 100%; }}
        a {{ color: {COLOR_PRINCIPAL}; text-decoration: none; font-weight: 500; }}
        a:hover {{ text-decoration: underline; }}
        li {{ margin-bottom: 15px; line-height: 1.5; }}
        
        /* ESTILO REVERTIDO: LIMPIO, SIN COLOR DE FONDO NI BORDES */
        blockquote {{ 
            background: transparent; 
            border: none; 
            margin: 5px 0 0 0; 
            padding: 0 0 0 10px; 
            color: #666; 
            font-style: italic; 
            font-size: 0.95em;          
        }}
    """

    template = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Reporte {empresa}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-treemap@2.3.0/dist/chartjs-chart-treemap.min.js"></script>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Reporte Ejecutivo: {empresa}</h1>
                <div class="periodo">Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
            </div>
            <div class="nav-bar">
                <a href="#analisis-general" class="nav-btn">📈 Análisis General</a>
                <a href="#reporte-sentimiento" class="nav-btn">📊 Sentimiento</a>
                <a href="#panorama-nacional" class="nav-btn">{flag_img} Nacional</a>
                <a href="#panorama-internacional" class="nav-btn">🌍 Internacional</a>
                <a href="#resumen-digital" class="nav-btn">💬 Redes Sociales</a>
                <a href="#detalle-noticias" class="nav-btn">📰 Noticias</a>
            </div>
            {html_content}
        </div>
        <script>
            Chart.register(ChartDataLabels);
            Chart.defaults.font.family = 'Roboto';
            const labelConfig = {{ color: '#fff', font: {{ weight: 'bold' }}, formatter: (v) => v > 0 ? v : '' }};
            const colors = ['#2E7D32', '#FBC02D', '#D32F2F'];

            const genSent = {metrics['gen']};
            const brandRaw = {metrics['brands']}; 
            const brandLabels = ['Adecoagro', 'Pilagá', 'Molinos Ala', 'La Lácteo'];
            const socVol = {metrics['soc_vol']}; 
            const socSent = {metrics['soc_sent']};

            new Chart(document.getElementById('chartGenSent'), {{
                type: 'doughnut',
                data: {{ labels: ['Positivo', 'Neutro', 'Negativo'], datasets: [{{ data: genSent, backgroundColor: colors, borderWidth: 0 }}] }},
                options: {{ maintainAspectRatio: false, cutout: '60%', plugins: {{ legend: {{ position: 'right' }}, datalabels: labelConfig }} }}
            }});

            const brandDataClean = [];
            const brandLabelsClean = [];
            const brandColors = ['#1976D2', '#00796B', '#F57C00', '#7B1FA2'];
            const brandColorsClean = [];

            brandRaw.forEach((val, idx) => {{
                if (val > 0) {{
                    brandDataClean.push(val);
                    brandLabelsClean.push(brandLabels[idx]);
                    brandColorsClean.push(brandColors[idx]);
                }}
            }});

            if (brandDataClean.length > 0) {{
                new Chart(document.getElementById('chartBrandVol'), {{
                    type: 'bar',
                    data: {{ 
                        labels: brandLabelsClean, 
                        datasets: [{{ 
                            data: brandDataClean, 
                            backgroundColor: brandColorsClean, 
                            barPercentage: 0.6 
                        }}] 
                    }},
                    options: {{ maintainAspectRatio: false, indexAxis: 'y', plugins: {{ legend: {{ display: false }}, datalabels: {{ anchor: 'end', align: 'end', color: '#555' }} }}, scales: {{ x: {{ display: false, grace: '15%' }}, y: {{ grid: {{ display: false }} }} }} }}
                }});
            }} else {{
                document.getElementById('chartBrandVol').parentNode.innerHTML = '<p style="padding-top:80px;color:#999;text-align:center;">Sin menciones de marca</p>';
            }}

            const treeCtx = document.getElementById('chartSocTree');
            if (treeCtx) {{
                const rawData = [
                    {{ category: 'Facebook', value: socVol[0] }},
                    {{ category: 'Instagram', value: socVol[1] }},
                    {{ category: 'X (Twitter)', value: socVol[2] }},
                    {{ category: 'TikTok', value: socVol[3] }},
                    {{ category: 'YouTube', value: socVol[4] }}
                ].filter(d => d.value > 0); 

                if (rawData.length > 0) {{
                    new Chart(treeCtx, {{
                        type: 'treemap',
                        data: {{
                            datasets: [{{
                                tree: rawData,
                                key: 'value',
                                groups: ['category'],
                                backgroundColor: (ctx) => {{
                                    if(ctx.type !== 'data') return 'transparent';
                                    const map = {{ 'Facebook': '#1877F2', 'Instagram': '#C13584', 'X (Twitter)': '#000000', 'TikTok': '#00F2EA', 'YouTube': '#FF0000' }};
                                    return map[ctx.raw._data.category] || '#999';
                                }},
                                labels: {{ display: true, color: 'white', font: {{ weight: 'bold', size: 12 }} }}
                            }}]
                        }},
                        options: {{ maintainAspectRatio: false, plugins: {{ legend: {{ display: false }}, datalabels: {{ display: false }} }} }}
                    }});
                }} else {{ treeCtx.parentNode.innerHTML = '<p style="padding-top:80px; color:#999; text-align:center;">Sin actividad en redes</p>'; }}
            }}

            new Chart(document.getElementById('chartSocSent'), {{
                type: 'bar',
                data: {{ labels: ['Pos', 'Neu', 'Neg'], datasets: [{{ data: socSent, backgroundColor: colors }}] }},
                options: {{ maintainAspectRatio: false, plugins: {{ legend: {{ display: false }}, datalabels: {{ anchor: 'end', align: 'end', color: '#555' }} }}, scales: {{ y: {{ display: false, grace: '15%' }}, x: {{ grid: {{ display: false }} }} }} }}
            }});
        </script>
    </body>
    </html>
    """
    
    filename = f"reporte_{empresa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(template)
    
    print(f"✅ Reporte generado: {filename}")
    webbrowser.open(f"file://{os.path.abspath(filename)}")