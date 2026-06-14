import pandas as pd
import plotly.express as px

# Cargar datos
df = pd.read_csv(
    r"C:\Users\Benjamin\Downloads\anime_watchers_dataset_10000.csv"
)


# =========================
# FILTRAR SOLO 2023 + ISEKAI
# =========================
df_isekai = df[
    (df["Start_Year_Watching"] == 2023) &
    (df["Favorite_Anime_Genre"] == "Isekai")
]

# =========================
# GASTO POR PAÍS
# =========================
mapa = (
    df_isekai.groupby("Country", as_index=False)
    ["Merchandise_Spending_USD"]
    .sum()
    .rename(columns={
        "Merchandise_Spending_USD": "Gasto en mercancías (USD)_2023"
    })
)

print(mapa.head())

# =========================
# MAPA
# =========================
fig = px.choropleth(
    mapa,
    locations="Country",
    locationmode="country names",
    color="Gasto en mercancías (USD)_2023",
    hover_name="Country",
    hover_data={
        "Gasto en mercancías (USD)_2023": ":,.0f"
    },
    color_continuous_scale="Viridis",
    title="Gasto en mercancías (USD) de Anime Isekai por País (2023)"
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True
    )
)

fig.show()