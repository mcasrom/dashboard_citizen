"""
mapa_ccaa.py — Mapas Choropleth CCAA España (GeoJSON embebido)
CitizenWatch Pro / SIEG — Miguel Castillo
Uso: import mapa_ccaa as mc; fig = mc.mapa_indicador(df, col_ccaa, col_valor, titulo)
"""
import json
import pandas as pd
import plotly.graph_objects as go

# ── Normalización de nombres CCAA ────────────────────────────
# Mapa canónico → variantes comunes
_ALIAS = {
    "Andalucía":            ["andalucia", "andalucía"],
    "Aragón":               ["aragon", "aragón"],
    "Asturias":             ["principado de asturias", "asturias"],
    "Baleares":             ["illes balears", "baleares", "islas baleares"],
    "Canarias":             ["canarias"],
    "Cantabria":            ["cantabria"],
    "Castilla y León":      ["castilla y leon", "castilla y león", "castilla-y-leon"],
    "Castilla-La Mancha":   ["castilla-la mancha", "castilla la mancha"],
    "Cataluña":             ["cataluna", "cataluña", "catalunya"],
    "C. Valenciana":        ["comunitat valenciana", "comunidad valenciana",
                             "c. valenciana", "valenciana", "valencia"],
    "Extremadura":          ["extremadura"],
    "Galicia":              ["galicia"],
    "La Rioja":             ["la rioja", "rioja"],
    "Madrid":               ["comunidad de madrid", "madrid"],
    "Murcia":               ["region de murcia", "región de murcia", "murcia"],
    "Navarra":              ["comunidad foral de navarra", "navarra"],
    "País Vasco":           ["pais vasco", "país vasco", "euskadi"],
    "Ceuta":                ["ceuta"],
    "Melilla":              ["melilla"],
}

def _normaliza(nombre: str) -> str:
    """Devuelve nombre canónico dado cualquier variante."""
    n = nombre.strip().lower()
    for canon, variantes in _ALIAS.items():
        if n in variantes or n == canon.lower():
            return canon
    return nombre.strip()  # si no matchea, devuelve tal cual

# ── GeoJSON CCAA España (simplificado, embebido) ─────────────
# Geometrías aproximadas como polígonos simples para no depender
# de URLs externas. Suficiente para colorear en Plotly.
# Coordenadas: bounding-box aproximado por CCAA.

_GEOJSON = {
  "type": "FeatureCollection",
  "features": [
    {"type":"Feature","id":"Andalucía",
     "properties":{"name":"Andalucía"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-7.5,38.2],[-7.5,36.0],[-5.6,35.9],[-2.0,36.5],
       [-1.6,37.4],[-0.2,37.5],[0.3,38.1],[-1.0,38.9],
       [-3.0,38.9],[-4.5,38.5],[-6.5,38.5],[-7.5,38.2]
     ]]}},
    {"type":"Feature","id":"Aragón",
     "properties":{"name":"Aragón"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-2.0,43.7],[-0.3,43.7],[0.8,42.8],[0.8,40.5],
       [-1.0,40.0],[-2.0,40.3],[-2.5,41.5],[-2.0,43.7]
     ]]}},
    {"type":"Feature","id":"Asturias",
     "properties":{"name":"Asturias"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-7.1,43.8],[-4.5,43.8],[-4.5,43.0],[-6.0,43.0],[-7.1,43.8]
     ]]}},
    {"type":"Feature","id":"Baleares",
     "properties":{"name":"Baleares"},
     "geometry":{"type":"Polygon","coordinates":[[
       [1.2,39.1],[4.3,39.1],[4.3,38.6],[1.2,38.6],[1.2,39.1]
     ]]}},
    {"type":"Feature","id":"Canarias",
     "properties":{"name":"Canarias"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-18.2,29.4],[-13.3,29.4],[-13.3,27.6],[-18.2,27.6],[-18.2,29.4]
     ]]}},
    {"type":"Feature","id":"Cantabria",
     "properties":{"name":"Cantabria"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-4.5,43.5],[-3.2,43.5],[-3.2,42.9],[-4.5,42.9],[-4.5,43.5]
     ]]}},
    {"type":"Feature","id":"Castilla y León",
     "properties":{"name":"Castilla y León"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-7.0,43.0],[-2.5,43.0],[-2.0,41.5],[-2.0,40.3],
       [-4.0,39.9],[-6.5,40.0],[-7.0,40.5],[-7.0,43.0]
     ]]}},
    {"type":"Feature","id":"Castilla-La Mancha",
     "properties":{"name":"Castilla-La Mancha"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-5.0,40.7],[-1.5,40.7],[-1.0,39.5],[-0.2,38.5],
       [-1.6,37.4],[-3.0,38.0],[-4.5,38.5],[-5.0,40.0],[-5.0,40.7]
     ]]}},
    {"type":"Feature","id":"Cataluña",
     "properties":{"name":"Cataluña"},
     "geometry":{"type":"Polygon","coordinates":[[
       [0.8,42.8],[3.3,42.8],[3.3,40.5],[0.8,40.5],[0.8,42.8]
     ]]}},
    {"type":"Feature","id":"C. Valenciana",
     "properties":{"name":"C. Valenciana"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-1.0,40.0],[0.5,40.0],[0.5,37.8],[-1.6,37.4],[-1.0,40.0]
     ]]}},
    {"type":"Feature","id":"Extremadura",
     "properties":{"name":"Extremadura"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-7.5,40.5],[-5.0,40.5],[-5.0,38.5],[-7.5,38.2],[-7.5,40.5]
     ]]}},
    {"type":"Feature","id":"Galicia",
     "properties":{"name":"Galicia"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-9.3,43.8],[-7.0,43.8],[-7.0,43.0],[-7.0,41.8],[-9.3,43.0],[-9.3,43.8]
     ]]}},
    {"type":"Feature","id":"La Rioja",
     "properties":{"name":"La Rioja"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-3.1,42.6],[-2.0,42.6],[-2.0,41.9],[-3.1,41.9],[-3.1,42.6]
     ]]}},
    {"type":"Feature","id":"Madrid",
     "properties":{"name":"Madrid"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-4.6,40.9],[-3.1,40.9],[-3.1,39.9],[-4.6,39.9],[-4.6,40.9]
     ]]}},
    {"type":"Feature","id":"Murcia",
     "properties":{"name":"Murcia"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-2.0,38.5],[-0.6,38.5],[-0.6,37.4],[-2.0,37.4],[-2.0,38.5]
     ]]}},
    {"type":"Feature","id":"Navarra",
     "properties":{"name":"Navarra"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-2.0,43.3],[-0.8,43.3],[-0.8,42.0],[-2.0,42.0],[-2.0,43.3]
     ]]}},
    {"type":"Feature","id":"País Vasco",
     "properties":{"name":"País Vasco"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-3.5,43.5],[-1.8,43.5],[-1.8,42.5],[-3.5,42.5],[-3.5,43.5]
     ]]}},
    {"type":"Feature","id":"Ceuta",
     "properties":{"name":"Ceuta"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-5.37,35.91],[-5.27,35.91],[-5.27,35.85],[-5.37,35.85],[-5.37,35.91]
     ]]}},
    {"type":"Feature","id":"Melilla",
     "properties":{"name":"Melilla"},
     "geometry":{"type":"Polygon","coordinates":[[
       [-2.97,35.31],[-2.91,35.31],[-2.91,35.27],[-2.97,35.27],[-2.97,35.31]
     ]]}},
  ]
}

# ── Paletas por tipo de indicador ────────────────────────────
_PALETAS = {
    "paro":      "Reds",        # más rojo = peor
    "vivienda":  "YlOrRd",      # más rojo = más caro
    "sanidad":   "RdYlGn_r",    # más rojo = peor (más espera)
    "corrupcion":"RdYlGn_r",
    "default":   "Blues",
}

_PLOT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c9d1d9", family="Inter", size=12),
    margin=dict(l=0, r=0, t=40, b=0),
)

# ── Función principal ────────────────────────────────────────
def mapa_indicador(
    df: pd.DataFrame,
    col_ccaa: str,
    col_valor: str,
    titulo: str = "",
    unidad: str = "%",
    tipo: str = "default",
    invertir: bool = False,
    height: int = 520,
) -> go.Figure:
    """
    Genera un mapa Choropleth coloreado por CCAA.

    Parámetros:
    - df       : DataFrame con al menos col_ccaa y col_valor
    - col_ccaa : nombre columna con nombres de CCAA
    - col_valor: nombre columna numérica
    - titulo   : título del mapa
    - unidad   : sufijo para tooltip (%, €, días…)
    - tipo     : 'paro' | 'vivienda' | 'sanidad' | 'corrupcion' | 'default'
    - invertir : True = mejor = más alto (verde arriba)
    - height   : altura en px
    """
    df = df.copy()
    df[col_ccaa] = df[col_ccaa].apply(_normaliza)
    df[col_valor] = pd.to_numeric(df[col_valor], errors="coerce")

    paleta = _PALETAS.get(tipo, "Blues")
    if invertir:
        paleta = paleta + "_r" if not paleta.endswith("_r") else paleta[:-2]

    fig = go.Figure(go.Choropleth(
        geojson=_GEOJSON,
        locations=df[col_ccaa],
        z=df[col_valor],
        featureidkey="id",
        colorscale=paleta,
        marker_line_color="#30363d",
        marker_line_width=1.2,
        colorbar=dict(
            title=dict(text=unidad, font=dict(color="#c9d1d9", size=11)),
            tickfont=dict(color="#c9d1d9", size=10),
            bgcolor="rgba(22,27,34,0.8)",
            bordercolor="#30363d",
            borderwidth=1,
            thickness=14,
            len=0.7,
        ),
        text=df[col_ccaa],
        customdata=df[[col_ccaa, col_valor]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            f"<b>%{{customdata[1]:.1f}}{unidad}</b><extra></extra>"
        ),
        zauto=True,
    ))

    fig.update_geos(
        visible=False,
        fitbounds="locations",
        projection_type="natural earth",
        bgcolor="rgba(0,0,0,0)",
        showcoastlines=True, coastlinecolor="#30363d",
        showland=True, landcolor="rgba(22,27,34,0.5)",
        showocean=True, oceancolor="rgba(13,17,23,0.8)",
        showlakes=False,
        showframe=False,
    )

    fig.update_layout(
        **_PLOT_BASE,
        height=height,
        title=dict(
            text=titulo,
            font=dict(color="white", size=14),
            x=0.02,
        ),
        geo=dict(
            scope="europe",
            fitbounds="locations",
            bgcolor="rgba(0,0,0,0)",
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#30363d",
            showland=True,
            landcolor="rgba(22,27,34,0.4)",
            showocean=True,
            oceancolor="rgba(13,17,23,0.9)",
            showlakes=False,
            showsubunits=True,
            subunitcolor="#30363d",
            center=dict(lon=-3.7, lat=40.4),
            projection_scale=5.5,
        ),
    )
    return fig


# ── Funciones específicas por tab ────────────────────────────

def mapa_paro_ccaa(df: pd.DataFrame) -> go.Figure:
    """Mapa tasa de paro por CCAA. df debe tener columnas ccaa, tasa_paro."""
    return mapa_indicador(
        df, "ccaa", "tasa_paro",
        titulo="Tasa de paro EPA 2025T3 (%)",
        unidad="%", tipo="paro", height=500,
    )


def mapa_vivienda_ccaa(df: pd.DataFrame = None) -> go.Figure:
    """Mapa precio vivienda €/m² por CCAA."""
    if df is None:
        datos = {
            "ccaa": [
                "Madrid","Baleares","Cataluña","País Vasco","Canarias",
                "Navarra","C. Valenciana","Andalucía","Cantabria",
                "Murcia","Galicia","Aragón","Castilla y León",
                "Castilla-La Mancha","Extremadura","La Rioja","Asturias",
            ],
            "precio_m2": [
                4800,4200,3100,2850,2100,1920,1820,1650,1580,
                1240,1290,1420,1150,980,860,1050,1180,
            ],
        }
        df = pd.DataFrame(datos)
    return mapa_indicador(
        df, "ccaa", "precio_m2",
        titulo="Precio vivienda €/m² — Idealista/BdE 2025",
        unidad="€/m²", tipo="vivienda", height=500,
    )


def mapa_sanidad_ccaa(df: pd.DataFrame = None) -> go.Figure:
    """Mapa días de espera quirúrgica media por CCAA."""
    if df is None:
        datos = {
            "ccaa": [
                "Madrid","Cataluña","Andalucía","C. Valenciana","País Vasco",
                "Galicia","Castilla y León","Aragón","Murcia","Canarias",
                "Asturias","Baleares","Navarra","Extremadura","Cantabria",
                "La Rioja","Castilla-La Mancha","Ceuta","Melilla",
            ],
            "dias_espera": [
                98,134,156,142,87,121,118,109,131,168,
                115,127,92,145,103,88,122,201,188,
            ],
        }
        df = pd.DataFrame(datos)
    return mapa_indicador(
        df, "ccaa", "dias_espera",
        titulo="Días medios espera quirúrgica SNS 2025",
        unidad=" días", tipo="sanidad", height=500,
    )


def mapa_paro_juvenil_ccaa(df: pd.DataFrame = None) -> go.Figure:
    """Mapa paro juvenil (<25 años) por CCAA."""
    if df is None:
        datos = {
            "ccaa": [
                "Andalucía","Canarias","Murcia","Extremadura","Ceuta","Melilla",
                "C. Valenciana","Castilla-La Mancha","Galicia","Asturias",
                "Aragón","Cantabria","Madrid","Cataluña","La Rioja",
                "Baleares","Navarra","País Vasco","Castilla y León",
            ],
            "paro_juvenil": [
                42.1,38.4,35.2,40.8,55.1,51.3,
                32.4,31.8,28.9,27.4,
                22.1,24.8,19.2,21.5,18.4,
                20.1,17.8,15.9,22.6,
            ],
        }
        df = pd.DataFrame(datos)
    return mapa_indicador(
        df, "ccaa", "paro_juvenil",
        titulo="Paro juvenil <25 años por CCAA — EPA 2025 (%)",
        unidad="%", tipo="paro", height=500,
    )


def mapa_renta_ccaa(df: pd.DataFrame = None) -> go.Figure:
    """Mapa renta media por hogar por CCAA (€/año)."""
    if df is None:
        datos = {
            "ccaa": [
                "Madrid","País Vasco","Navarra","Cataluña","Baleares",
                "La Rioja","Cantabria","Aragón","Asturias","C. Valenciana",
                "Castilla y León","Galicia","Canarias","Murcia",
                "Castilla-La Mancha","Andalucía","Extremadura","Ceuta","Melilla",
            ],
            "renta_hogar": [
                36200,35800,34100,30400,29800,
                27900,27200,26800,25900,24700,
                24200,23800,22400,22100,
                21800,21200,19400,21600,20800,
            ],
        }
        df = pd.DataFrame(datos)
    return mapa_indicador(
        df, "ccaa", "renta_hogar",
        titulo="Renta media por hogar — INE ECV 2025 (€/año)",
        unidad="€/año", tipo="default", invertir=True, height=500,
    )


# ── Test standalone ──────────────────────────────────────────
if __name__ == "__main__":
    fig = mapa_vivienda_ccaa()
    fig.show()
    print("✅ mapa_ccaa.py OK — funciones disponibles:")
    print("  mapa_paro_ccaa(df)")
    print("  mapa_vivienda_ccaa(df=None)")
    print("  mapa_sanidad_ccaa(df=None)")
    print("  mapa_paro_juvenil_ccaa(df=None)")
    print("  mapa_renta_ccaa(df=None)")
    print("  mapa_indicador(df, col_ccaa, col_valor, ...)")
