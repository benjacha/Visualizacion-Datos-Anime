import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("AnimeList.csv")

# Eliminar filas sin género
df = df.dropna(subset=['genre', 'members'])

# Convertir a lista
df['genre_list'] = df['genre'].apply(lambda x: x.split(', '))

df_exploded = df.explode('genre_list')

cantidad = df_exploded.groupby('genre_list')['anime_id'].count()
vistas = df_exploded.groupby('genre_list')['members'].sum()

resultado = pd.DataFrame({
    'cantidad': cantidad,
    'vistas': vistas
}).reset_index()

plt.show()

# Top 10 géneros por vistas (para limpiar el gráfico)
resultado_top = resultado.sort_values('vistas', ascending=False).head(10)

# Normalizar
resultado_top['cantidad_norm'] = resultado_top['cantidad'] / resultado_top['cantidad'].max()
resultado_top['vistas_prom'] = resultado_top['vistas'] / resultado_top['cantidad']
resultado_top['vistas_prom_norm'] = resultado_top['vistas_prom'] / resultado_top['vistas_prom'].max()

# Ordenar para visual
resultado_top = resultado_top.sort_values('vistas_prom_norm')

plt.figure(figsize=(10, 6))

# Líneas 
for i in range(len(resultado_top)):
    plt.plot(
        [resultado_top['cantidad_norm'].iloc[i], resultado_top['vistas_prom_norm'].iloc[i]],
        [i, i],
        linewidth=2,
        color='skyblue',
        zorder=1   # más atrás
    )

# Puntos cantidad (naranjo)
plt.scatter(
    resultado_top['cantidad_norm'], 
    range(len(resultado_top)), 
    label="Cantidad",
    color='orange', 
    alpha=1,
    zorder=3   
)

# Puntos vistas (morado)
plt.scatter(
    resultado_top['vistas_prom_norm'], 
    range(len(resultado_top)), 
    label="Vistas",
    color='purple', 
    alpha=0.6,
    zorder=3  
)

# Etiquetas
plt.yticks(range(len(resultado_top)), resultado_top['genre_list'])

plt.xlabel("Valor normalizado")
plt.title("Top 10 Géneros: Cantidad vs Vistas")

plt.legend()
plt.grid(axis='x', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()
