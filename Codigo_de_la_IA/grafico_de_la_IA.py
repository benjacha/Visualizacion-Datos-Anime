import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -------------------------------
# 1. Cargar datasets
# -------------------------------
file1 = "C:\\Users\\Benjamin\\Desktop\\trabajos\\visualizacion de datos\\tarea 1\\mal_top2000_anime.csv"
file2 = "C:\\Users\\Benjamin\\Desktop\\trabajos\\visualizacion de datos\\tarea 1\\AnimeList.csv"
file3 = "C:\\Users\\Benjamin\\Desktop\\trabajos\\visualizacion de datos\\tarea 1\\Anime_ratings.csv"

def try_read(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

df1 = try_read(file1)
df2 = try_read(file2)
df3 = try_read(file3)

# -------------------------------
# 2. Normalizar columnas
# -------------------------------
def standardize(df):
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    df["title"] = None
    df["genres"] = None
    df["studio"] = None
    df["popularity"] = np.nan

    # título
    for c in df.columns:
        if c.lower() in ["title", "name", "anime_title"]:
            df["title"] = df[c]
            break

    # género
    for c in df.columns:
        if c.lower() in ["genres", "genre"]:
            df["genres"] = df[c].astype(str)
            break

    # estudio
    for c in df.columns:
        if c.lower() in ["studio", "studios", "producer"]:
            df["studio"] = df[c].astype(str)
            break

    # popularidad
    for c in df.columns:
        if c.lower() in ["members", "popularity", "scored_by"]:
            df["popularity"] = pd.to_numeric(df[c], errors="coerce")
            break

    return df[["title","genres","studio","popularity"]]

s1 = standardize(df1)
s2 = standardize(df2)
s3 = standardize(df3)

df = pd.concat([s1, s2, s3], ignore_index=True)

df["genres"] = df["genres"].fillna("")
df["studio"] = df["studio"].fillna("Unknown")

# -------------------------------
# 3. Expandir géneros (rápido)
# -------------------------------
df["genre"] = df["genres"].str.split(r"[,\|;]+")
df_exp = df.explode("genre")

df_exp["genre"] = df_exp["genre"].str.strip()
df_exp["genre"] = df_exp["genre"].replace("", "Unknown")

# -------------------------------
# 1. TOP géneros + "Otros"
# -------------------------------
top_n = 6
top_genres = df_exp["genre"].value_counts().head(top_n).index

df_exp["genre_grouped"] = df_exp["genre"].apply(
    lambda x: x if x in top_genres else "Otros géneros"
)

# -------------------------------
# 2. TOP estudios
# -------------------------------
top_studios = df_exp["studio"].value_counts().head(8).index

df_sankey = df_exp[
    df_exp["studio"].isin(top_studios)
].copy()

# -------------------------------
# 3. Niveles de popularidad
# -------------------------------
pop_q = df_sankey["popularity"].dropna()

low = pop_q.quantile(0.33)
high = pop_q.quantile(0.66)

def nivel_pop(p):
    if pd.isna(p):
        return None
    elif p <= low:
        return "Bajo"
    elif p <= high:
        return "Medio"
    else:
        return "Alto"

df_sankey["pop_level"] = df_sankey["popularity"].apply(nivel_pop)

# ❗ eliminar filas inválidas (esto evita el círculo raro)
df_sankey = df_sankey.dropna(subset=["genre_grouped", "studio", "pop_level"])

# -------------------------------
# 4. Crear conexiones
# -------------------------------
g_s = df_sankey.groupby(["genre_grouped","studio"]).size().reset_index(name="value")
s_p = df_sankey.groupby(["studio","pop_level"]).size().reset_index(name="value")

# -------------------------------
# 5. Crear nodos
# -------------------------------
genres_nodes = list(df_sankey["genre_grouped"].unique())
studio_nodes = list(top_studios)
pop_nodes = ["Bajo","Medio","Alto"]

nodes = genres_nodes + studio_nodes + pop_nodes
node_dict = {name:i for i,name in enumerate(nodes)}

# -------------------------------
# 6. Links
# -------------------------------
source = []
target = []
value = []

# Género → Estudio
for _, row in g_s.iterrows():
    if row["genre_grouped"] != row["studio"]:  # evitar loops raros
        source.append(node_dict[row["genre_grouped"]])
        target.append(node_dict[row["studio"]])
        value.append(row["value"])

# Estudio → Popularidad
for _, row in s_p.iterrows():
    source.append(node_dict[row["studio"]])
    target.append(node_dict[row["pop_level"]])
    value.append(row["value"])

# -------------------------------
# 7. Sankey limpio
# -------------------------------
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",  # 🔥 evita deformaciones raras
    node=dict(
        pad=20,
        thickness=18,
        line=dict(color="black", width=0.3),
        label=nodes
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color="rgba(150,150,150,0.4)"
    )
)])

fig.update_layout(
    title="Flujo: Género → Estudio → Nivel de Popularidad",
    font_size=12
)

fig.show()