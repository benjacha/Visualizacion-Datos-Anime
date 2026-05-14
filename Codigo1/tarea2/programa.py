import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def eliminar_parentesis(texto):
    resultado = ""
    nivel = 0

    for c in texto:
        if c == '(':
            nivel += 1
        elif c == ')':
            if nivel > 0:
                nivel -= 1
        else:
            if nivel == 0:
                resultado += c

    return resultado


def separar_valores(texto):
    if pd.isna(texto):
        return []

    texto = str(texto)
    limpio = eliminar_parentesis(texto)
    partes = limpio.split(',')
    return [p.strip() for p in partes if p.strip()]

# cambiar la ruta al archivo según la ubicacion de tu archivo
df = pd.read_excel(r"C:\Users\Benjamin\Desktop\trabajos\visualizacion de datos\tarea2\Encuesta sobre preferencias en Animes.csv\Encuesta sobre preferencias en Animes (respuestas).xlsx", usecols="B:E")
resultado = []
for _, row in df.iterrows():
    fila_dict = {}

    for col in df.columns:
        fila_dict[col] = separar_valores(row[col])

    resultado.append(fila_dict)

# Mostrar resultados (opcional, para verificar que se procesó correctamente)
#for i, r in enumerate(resultado):
#    print(f"Fila {i+1}: {r}")

def normalizar_fuente(f):
    f = f.lower()

    if "red" in f:
        return "Redes Sociales"
    elif "recomendación" in f:
        return "Recomendación"
    elif "stream" in f or "plataforma" in f:
        return "Streaming"
    elif "publicidad" in f:
        return "Publicidad"
    elif "videojuego" in f:
        return "Videojuegos"
    elif "ranking" in f or "catalog" in f:
        return "Ranking"
    
    return "Otros"

colores = {
    "Redes Sociales": "blue",
    "Recomendación": "green",
    "Streaming": "purple",
    "Publicidad": "orange",
    "Videojuegos": "red",
    "Ranking": "cyan",
    "Otros": "gray"
}

def color_frecuencia(freq):
    if "0-4" in freq: return "#d4f0ff"
    if "4-8" in freq: return "#92d5ff"
    if "8-16" in freq: return "#2fb4ff"
    if "+16" in freq: return "#006bb3"
    return "gray"

def frecuencia_a_valor(freq):
    if "0-4" in freq:
        return 4
    elif "4-8" in freq:
        return 8
    elif "8-16" in freq:
        return 16
    elif "+16" in freq:
        return 20
    return 4

#grafico 1
fig, ax = plt.subplots(figsize=(12,8))

y = 0

for fila in resultado:
    fuentes = fila['¿Cómo te enteras de nuevos Animes?']
    freq = fila['¿Con qué frecuencia consumes Anime a la semana?'][0]

    fuentes_norm = list(set(normalizar_fuente(f) for f in fuentes))
    largo = frecuencia_a_valor(freq)

    ancho = largo / len(fuentes_norm)

    x = 0
    for f in fuentes_norm:
        ax.add_patch(plt.Rectangle(
            (x, y), ancho, 0.8,
            color=colores.get(f, "gray")
        ))

        ax.text(x + ancho/2, y + 0.4, f[0],
                ha='center', va='center',
                fontsize=8, color='white')

        x += ancho

    y += 1
ax.set_yticks(range(y))
ax.set_yticklabels([f"P{i+1}" for i in range(y)])
ax.set_xlim(0, 20)

ax.set_xticks([0, 4, 8, 12 ,16, 20])
ax.set_xticklabels([
    "0",
    "4",
    "8",
    "12",
    "16",
    "mayor a 16"
])
ax.set_xlabel("Frecuencia horaria (horas por semana)")
ax.set_title("Fuentes de descubrimiento por persona según frecuencia")
legend_handles = [
    mpatches.Patch(color=color, label=label)
    for label, color in colores.items()
]

ax.legend(handles=legend_handles,
          title="Fuente de descubrimiento",
          bbox_to_anchor=(1.05, 1),
          loc='upper left')

plt.tight_layout()
plt.show()

#grafico 2
plataformas = sorted(set(p for fila in resultado for p in fila['¿En qué plataforma consumes Anime?']))
criterios = sorted(set(c for fila in resultado for c in fila['¿En qué te fijas a la hora de ver un anime?']))

matriz = np.zeros((len(plataformas), len(criterios)))

for fila in resultado:
    for p in fila['¿En qué plataforma consumes Anime?']:
        for c in fila['¿En qué te fijas a la hora de ver un anime?']:
            i = plataformas.index(p)
            j = criterios.index(c)
            matriz[i][j] += 1
cmap = plt.cm.get_cmap('tab20', len(plataformas))
colores_plataforma = {p: cmap(i) for i, p in enumerate(plataformas)}

fig, ax = plt.subplots(figsize=(12,8))
for i, p in enumerate(plataformas):
    for j in range(len(criterios)):
        valor = matriz[i][j]

        if valor > 0:
            ax.scatter(
                j, i,
                s=valor * 80,
                color=colores_plataforma[p],
                alpha=0.7
            )
ax.set_xticks(range(len(criterios)))
ax.set_yticks(range(len(plataformas)))

ax.set_xticklabels(criterios, rotation=90)
ax.set_yticklabels(plataformas)

ax.set_title("Relación Plataforma vs Criterios (tamaño del circulo = frecuencia)")

plt.show()