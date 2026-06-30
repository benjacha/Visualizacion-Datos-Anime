import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import numpy as np

# -----------------------------
# 1. Cargar datos
# -----------------------------
df = pd.read_csv("C:\\Users\\Benjamin\\Desktop\\trabajos\\visualizacion de datos\\tarea 1\\mal_top2000_anime.csv")  # cambia el nombre si es distinto

# Verificar columnas
required_cols = ['Studio', 'Genres', 'Score']
if not all(col in df.columns for col in required_cols):
    print("Error: El CSV no contiene las columnas 'Studio', 'Genres' y/o 'Score'.")
    print("Columnas disponibles:", df.columns.tolist())
    exit()

# -----------------------------
# 2. Procesar Studio y Genres (explode)
# -----------------------------
df["Studio"] = df["Studio"].str.split(",")
df = df.explode("Studio")
df["Studio"] = df["Studio"].str.strip()

df["Genres"] = df["Genres"].str.split(",")
df = df.explode("Genres")
df["Genres"] = df["Genres"].str.strip()

df = df.dropna(subset=['Studio', 'Genres', 'Score'])

# -----------------------------
# 3. Filtrar solo los 20 estudios con más animes
# -----------------------------
studio_counts = df.groupby('Studio').size().sort_values(ascending=False)
top_studios = studio_counts.head(20).index
df = df[df['Studio'].isin(top_studios)]

# -----------------------------
# 4. Filtrar solo los 10 géneros más frecuentes (entre esos estudios)
# -----------------------------
genre_counts = df.groupby('Genres').size().sort_values(ascending=False)
top_genres = genre_counts.head(10).index
df = df[df['Genres'].isin(top_genres)]

# Si después de filtrar quedan pocos datos, muestra advertencia
if df.empty:
    print("No quedan datos después del filtrado. Ajusta los top N.")
    exit()

# -----------------------------
# 5. Agrupar por (Studio, Genres) para calcular éxito (score promedio)
# -----------------------------
agrupado = df.groupby(['Studio', 'Genres']).agg(
    count=('Score', 'size'),
    avg_score=('Score', 'mean')
).reset_index()

# -----------------------------
# 6. Construir el grafo con NetworkX
# -----------------------------
G = nx.Graph()

# Añadir nodos
estudios = agrupado['Studio'].unique()
generos = agrupado['Genres'].unique()
G.add_nodes_from(estudios, type='studio')
G.add_nodes_from(generos, type='genre')

# Añadir aristas
for _, row in agrupado.iterrows():
    G.add_edge(row['Studio'], row['Genres'], weight=row['avg_score'], count=row['count'])

if len(G.nodes) == 0:
    print("El grafo no tiene nodos. Revisa los filtros.")
    exit()

# -----------------------------
# 7. Calcular posiciones con spring layout
# -----------------------------
pos = nx.spring_layout(G, seed=42, k=1.0, iterations=50)  # k más grande separa nodos

# -----------------------------
# 8. Preparar datos para Plotly
# -----------------------------
node_x = []
node_y = []
node_text = []
node_color = []
node_size = []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    tipo = 'Estudio' if G.nodes[node]['type'] == 'studio' else 'Género'
    if tipo == 'Estudio':
        total_animes = agrupado[agrupado['Studio'] == node]['count'].sum()
        color = '#1f77b4'  # azul
    else:
        total_animes = agrupado[agrupado['Genres'] == node]['count'].sum()
        color = '#2ca02c'  # verde
    size = 15 + 5 * np.log1p(total_animes)  # tamaño más grande para mejor visibilidad
    node_size.append(size)
    node_color.append(color)
    node_text.append(f"{node}<br>Tipo: {tipo}<br>Animes asociados: {total_animes}")

# Aristas
edge_x = []
edge_y = []
edge_hover_text = []
min_weight = agrupado['avg_score'].min()
max_weight = agrupado['avg_score'].max()
range_weight = max_weight - min_weight if max_weight > min_weight else 1

for u, v, data in G.edges(data=True):
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])
    width = 1 + 7 * (data['weight'] - min_weight) / range_weight
    edge_hover_text.append(f"{u} – {v}<br>Score promedio: {data['weight']:.2f}<br>Animes: {data['count']}")

# Traza de aristas (líneas con grosor según score)
edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.8, color='#888'),
    hoverinfo='text',
    text=edge_hover_text,
    mode='lines'
)

# Traza de nodos
node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    text=[n for n in G.nodes()],
    textposition='top center',
    hoverinfo='text',
    hovertext=node_text,
    marker=dict(
        size=node_size,
        color=node_color,
        line=dict(width=1, color='#333')
    )
)

# -----------------------------
# 9. Visualización con Plotly
# -----------------------------
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title=dict(
                        text='Top 20 estudios y top 10 géneros: Éxito por género (grafo de fuerza)',
                        font=dict(size=18)
                    ),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=50),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=700,
                    width=1000
                ))

fig.show()
# fig.write_html("estudios_generos_network_top20.html")  # opcional