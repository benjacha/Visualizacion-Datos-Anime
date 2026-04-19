import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Extraccion del genero mas popular por año

df_ga = pd.read_csv("C:/Users/gtoma/Desktop/Anime_ratings.csv")

df_ga["Year"] = df_ga["Release Date"].str.extract(r'(\d{4})') # Se sacan las fechas
df_ga["Year"] = pd.to_numeric(df_ga["Year"], errors="coerce").astype("Int64")

df_ga = df_ga.dropna(subset=["Year", "Genres", "Popularity"]) # sacamos los nan de las fechas

df_gen = df_ga[['Year', 'Genres', 'Popularity']].copy()
df_gen = df_gen.dropna()

df_gen = df_gen.assign(Genres=df_gen['Genres'].str.split(",")) # separamos los generos

df_gen["num_genres"] = df_gen["Genres"].apply(len) # cantidad de veces que aparece cada generos
df_gen_exp = df_gen.explode('Genres') # hacemos repetidos de animes pero por genero

df_gen_exp["Genres"] = df_gen_exp["Genres"].str.strip() 

df_gen_exp["pop"] = (1 / np.log(df_gen_exp["Popularity"] + 1)) / df_gen_exp["num_genres"]

popularidad = (
    df_gen_exp.groupby(["Year", "Genres"])["pop"]
    .sum()
    .reset_index()
)

top_por_año = popularidad.loc[
    popularidad.groupby("Year")["pop"].idxmax()
]

# Extraccion del Top anime por genero historico

# Expandir géneros, pero conservando Title y Rank
df_tg = df_ga[['Title', 'Year', 'Genres', 'Rank', 'Score']].copy()

df_tg["Rank"] = pd.to_numeric(df_tg["Rank"], errors="coerce")
df_tg["Score"] = pd.to_numeric(df_tg["Score"], errors="coerce")

# eliminacion de filas inválidas
df_tg = df_tg.dropna(subset=['Year', 'Genres', 'Rank'])

# Expansion de generos
df_tg = df_tg.assign(Genres=df_tg['Genres'].str.split(","))
df_tg = df_tg.explode('Genres')
df_tg['Genres'] = df_tg['Genres'].str.strip()

# Top anime por genero
df_best = (
    df_tg.sort_values('Rank')
    .groupby('Genres', as_index=False)
    .first()
    [['Genres', 'Year', 'Rank', 'Score', 'Title']]
    .rename(columns={
        'Title': 'title',
        'Genres': 'genre',
        'Rank': 'rank',
        'Score': 'score'
    })
    .sort_values('rank')
    .reset_index(drop=True)
)

# Grafica

pivot = popularidad.pivot(index="Year", columns="Genres", values="pop").fillna(0)
pivot = pivot.sort_index()

top_genres = pivot.sum().sort_values(ascending=False).head(9).index
pivot = pivot[top_genres]

pivot = pivot.rolling(window=5, min_periods=1).mean()
pivot = pivot.div(pivot.sum(axis=1), axis=0)

# Ranking
rank = pivot.rank(axis=1, ascending=False, method="min")

# TOP ANIME DESDE df_best
top_titles = df_best.set_index("genre")["title"]
top_scores = df_best.set_index("genre")["score"]
top_ranks = df_best.set_index("genre")["rank"]

top_titles = top_titles[top_genres]
top_scores = top_scores[top_genres]
top_ranks = top_ranks[top_genres]

# GRÁFICO
plt.figure(figsize=(14,6))

for genre in top_genres:
    plt.plot(rank.index, rank[genre], linewidth=2, label=genre)

plt.gca().invert_yaxis()

# AÑADIR TOP ANIME AL FINAL
last_year = rank.index[-1]

for i, genre in enumerate(top_genres):
    y_final = rank[genre].iloc[-1]
    x_plot = last_year + 1

    # tamaño según score
    size = 60 + 200 * (top_scores[genre] / 10)

    # punto
    plt.scatter(
        x_plot,
        y_final,
        s=size,
        edgecolor="black",
        zorder=5
    )

    # offset para evitar choque
    offset = (i - len(top_genres)/2) * 0.15

    label = f"{top_titles[genre][:20]} (#{int(top_ranks[genre])})"

    plt.text(
        x_plot + 0.4,
        y_final + offset,
        label,
        fontsize=8,
        va="center"
    )

years = rank.index
step = max(1, len(years)//12)

ticks = list(years[::step]) + [last_year + 1]
labels = [str(y) for y in years[::step]] + ["Top"]

plt.xticks(ticks, labels, rotation=45)

plt.title("Ranking de géneros en el tiempo y Anime más representativo historico por género")
plt.xlabel("Año")
plt.ylabel("Posición (1 = más popular)")

plt.legend(ncol=2)
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()