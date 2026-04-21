import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ---------------------------------------------------------
# 1. Carga y Estandarización (Limpieza de Repetidos)
# ---------------------------------------------------------

# Cargar archivos
df_st = pd.read_csv("mal_top2000_anime.csv")    
df_rt = pd.read_csv("Anime_ratings.csv")         
df_pl = pd.read_csv("AnimeList.csv")             

# Renombrar columnas a estándar 'Title'
df_st = df_st.rename(columns={'Name': 'Title'})
df_pl = df_pl.rename(columns={'title': 'Title'})

# Estandarizar textos y eliminar nulos en títulos
for df in [df_st, df_rt, df_pl]:
    df['Title'] = df['Title'].astype(str).str.strip().str.lower()
    # ELIMINAR REPETIDOS EN CADA ARCHIVO: Nos quedamos con la primera aparición de cada título
    df.drop_duplicates(subset=['Title'], keep='first', inplace=True)

# Cruce de datos (Merge)
df_master = pd.merge(df_st, df_rt, on='Title', how='inner')
df_master = pd.merge(df_master, df_pl, on='Title', how='inner')

# ELIMINAR REPETIDOS TRAS EL MERGE: Por si el cruce generó filas duplicadas
df_master.drop_duplicates(subset=['Title'], inplace=True)

# ---------------------------------------------------------
# 2. Preparación de Niveles (Limpieza de Corchetes y Nodos)
# ---------------------------------------------------------

# Función para limpiar ['ACTION'] -> ACTION
def limpiar_texto_sucio(col):
    # Elimina corchetes [ ], comillas ' y espacios
    return col.astype(str).str.replace(r"[\[\]']", "", regex=True).str.split(',').str[0].str.strip()

df_master['Main_Studio'] = limpiar_texto_sucio(df_master['Studio'])
df_master['Main_Genre'] = limpiar_texto_sucio(df_master['Genres_x'])

# Definir niveles de Dominancia (Percentiles)
q3 = df_master['members'].quantile(0.75)
q1 = df_master['members'].quantile(0.25)

def categorizar_dominancia(m):
    if m >= q3: return "ALTO IMPACTO (DOMINANTE)"
    if m >= q1: return "IMPACTO MEDIO"
    return "NICHO / BAJO IMPACTO"

df_master['Dominancia'] = df_master['members'].apply(categorizar_dominancia)

# ---------------------------------------------------------
# 3. Creación del Diagrama de Sankey
# ---------------------------------------------------------

def crear_visualizacion_sankey(df):
    # Seleccionamos los 10 estudios y 10 géneros con más presencia
    top_studios = df['Main_Studio'].value_counts().head(10).index.tolist()
    top_genres = df['Main_Genre'].value_counts().head(10).index.tolist()
    niveles_exito = [
        "ALTO IMPACTO (DOMINANTE)",
        "IMPACTO MEDIO",
        "NICHO / BAJO IMPACTO"
    ]

    # Mapear todos los nombres a índices numéricos para Plotly
    nodos = top_studios + top_genres + niveles_exito
    mapa_nodos = {nombre: i for i, nombre in enumerate(nodos)}

    fuentes, destinos, valores = [], [], []

    # FLUJO A: De Estudio a Género (Capacidad de Producción)
    for s in top_studios:
        for g in top_genres:
            cantidad = len(df[(df['Main_Studio'] == s) & (df['Main_Genre'] == g)])
            if cantidad > 0:
                fuentes.append(mapa_nodos[s])
                destinos.append(mapa_nodos[g])
                valores.append(cantidad)

    # FLUJO B: De Género a Dominancia (Efectividad del contenido)
    for g in top_genres:
        for ex in niveles_exito:
            cantidad = len(df[(df['Main_Genre'] == g) & (df['Dominancia'] == ex)])
            if cantidad > 0:
                fuentes.append(mapa_nodos[g])
                destinos.append(mapa_nodos[ex])
                valores.append(cantidad)

    # Configuración estética del gráfico
    # 🎨 colores de nodos
    node_colors = (
        ["#1199ED"] * len(top_studios) +   
        ["#11DEED"] * len(top_genres) +    
        ["#11EDB2"] * len(niveles_exito)
    )

    # 🔧 función
    def hex_to_rgba(hex_color, alpha=0.3):
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    # 🎨 colores de links
    link_colors = [
        hex_to_rgba(node_colors[s], 0.3)
        for s in fuentes
    ]

    # posiciones X (solo para separar columnas)
    x = (
        [0.1] * len(top_studios) +   # estudios
        [0.5] * len(top_genres) +    # géneros
        [0.9] * len(niveles_exito)   # impacto
    )

    # posiciones Y (solo impactos fijos)
    y = (
        [None] * len(top_studios) +
        [None] * len(top_genres) +
        [0.1, 0.5, 0.9]  # 🔥 ALTO, MEDIO, BAJO
    )

    fig = go.Figure(data=[go.Sankey(
        arrangement="fixed",

        node=dict(
            pad=15,
            thickness=25,
            line=dict(color="black", width=0.5),
            label=[n.upper() for n in nodos],
            color=node_colors,
            x=x,
            y=y
        ),

        link=dict(
            source=fuentes,
            target=destinos,
            value=valores,
            color=link_colors
        )
    )])
    fig.update_layout(
        title_text="<b>MAPA DE DOMINANCIA INDUSTRIAL</b><br>Trayectoria desde la Casa Productora hasta el Éxito de Mercado",
        font_size=11, width=1200, height=800
    )
    
    fig.show()
    # fig.write_html("dominancia_sankey.html") # Descomenta para guardar como archivo

crear_visualizacion_sankey(df_master)
