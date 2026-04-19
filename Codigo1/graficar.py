import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#instalar matplotlib y pandas para graficar
#pip install pandas
#pip install matplotlib seaborn

df = pd.read_csv("C:\\Users\\Benjamin\\Desktop\\trabajos\\visualizacion de datos\\tarea 1\\mal_top2000_anime.csv")  # cambia el nombre si es distinto

# Separar por coma
df["Studio"] = df["Studio"].str.split(",")

# Expandir filas (cada estudio en su propia fila)
df = df.explode("Studio")

# Limpiar espacios
df["Studio"] = df["Studio"].str.strip()
studios = df["Studio"].dropna().unique()

#print(len(studios)) #son 314 studios por lo que se tomaron solo los 30 primeros para que el gráfico sea legible

df["Popularity_Score"] = 1 / df["Popularity Rank"]
max_rank = df["Popularity Rank"].max()
df["Popularity_Score"] = max_rank - df["Popularity Rank"]

#preparar datos
# Cantidad de anime por estudio
cantidad = df["Studio"].value_counts()

# Popularidad promedio
popularidad = df.groupby("Studio")["Popularity_Score"].mean()

# Unir
data = pd.DataFrame({
    "Cantidad": cantidad,
    "Popularidad": popularidad
}).dropna()

# Top estudios (para que sea legible)
data = data.sort_values("Cantidad", ascending=False).head(30)

data["Cantidad_norm"] = data["Cantidad"] / data["Cantidad"].max()

#Grafico radial
labels = data.index
n = len(labels)

angulos = np.linspace(0, 2*np.pi, n, endpoint=False)

cantidad_vals = data["Cantidad_norm"].values
data["Popularidad_norm"] = data["Popularidad"] / data["Popularidad"].max()
popularidad_vals = data["Popularidad_norm"].values

# cerrar el círculo
angulos = np.append(angulos, angulos[0])
cantidad_vals = np.append(cantidad_vals, cantidad_vals[0])
popularidad_vals = np.append(popularidad_vals, popularidad_vals[0])

plt.figure(figsize=(16, 16))  # tamaño grande
ax = plt.subplot(111, polar=True)

# línea cantidad
ax.plot(angulos, cantidad_vals, linewidth=2, label="Cantidad de anime producidos")
ax.fill(angulos, cantidad_vals, alpha=0.2)

# línea popularidad
ax.plot(angulos, popularidad_vals, linewidth=2, linestyle="dashed", label="Popularidad promedio de sus animes")
ax.fill(angulos, popularidad_vals, alpha=0.2)

ax.set_xticks(angulos[:-1])
ax.set_xticklabels(labels)
ax.set_ylim(0, 1)
ax.set_yticks([0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(["25%", "50%", "75%", "100%"])
ax.tick_params(pad=15)


plt.title("Estudios: Cantidad vs Popularidad\n")

plt.legend(
    loc="upper right",
    bbox_to_anchor=(1.3, 1.1),
    title="Escala normalizada\n(0%–100% respecto al máximo)"
)

plt.show()