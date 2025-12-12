# config.py

# ============================================================
# CONFIGURACIÓN DEL PROYECTO
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# Si no encuentra la variable en el .env, usa "Empresa Genérica" por defecto
EMPRESA = os.getenv("TARGET_COMPANY", "AdecoAgro") 

# Lista de subsidiarias o marcas relacionadas
EMPRESAS_RELACIONADAS = ["Pilagá", "Molinos Ala", "La Lácteo"] 

# Activa el diagnóstico de dependencias (True/False)
DIAGNOSTICO_ACTIVADO = False

# Parámetros de búsqueda
DIAS_BUSQUEDA = 2
EMPRESA = "Adecoagro"
MIN_NOTICIAS = 5
MAX_NOTICIAS = 30

# Empresas relacionadas/subsidiarias de Adecoagro (Nombres para búsqueda)
EMPRESAS_RELACIONADAS = [
    "Adeco Agropecuaria S.A.",
    "Pilagá S.A.",
    "Molinos Libres S.A.",
    "Cavok S.A.",
    "Establecimientos El Orden S.A.",
    "Bañado del Salado S.A.",
    "Agro Invest S.A.",
    "Forsalta S.A.",
    "Molinos Ala",
    "Las Tres Niñas",
    "Angelita",
    "Mani del plata",
    "Energia Agro Sau"
]

# Fuentes priorizadas por país
FUENTES_ARGENTINA = [
    "clarin.com", "lanacion.com.ar", "infobae.com", "ambito.com",
    "agronegocios.com.ar", "bolsar.com", "infocampo.com.ar",
    "elcronista.com", "perfil.com", "pagina12.com.ar", "mercado.com.ar"
]

TERMINOS_SECTOR = [
    "Sancor crisis",
    "La Serenísima lechería",
    "Atilra gremio lechero",
    "Cosecha arroz argentina",
    "Sector agropecuario sequía"
]

# Colores de la marca Adecoagro
COLOR_PRINCIPAL = "#2E7D32"  # Verde oscuro
COLOR_SECUNDARIO = "#FFC107"  # Amarillo trigo
COLOR_FONDO = "#F5F5F5"  # Gris claro
COLOR_TEXTO = "#212121"  # Gris oscuro
