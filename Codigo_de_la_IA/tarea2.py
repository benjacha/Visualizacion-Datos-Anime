import pandas as pd
import plotly.express as px

# Datos sintetizados basados en las 21 respuestas cruzando Plataforma (Top 3) y Atributos (Top 5)
data = {
    'Atributo': ['Narrativa', 'Animación', 'Diseño de Personajes', 'Banda Sonora', 'Género'] * 3,
    'Plataforma': ['Netflix']*5 + ['Animeflv']*5 + ['Crunchyroll']*5,
    'Votos': [
        8, 7, 5, 6, 8,  # Perfil de los usuarios que ven en Netflix
        7, 9, 8, 4, 9,  # Perfil de los usuarios que ven en Animeflv
        6, 8, 5, 7, 6   # Perfil de los usuarios que ven en Crunchyroll
    ]
}

df = pd.DataFrame(data)

# Creación del Gráfico de Radar usando coordenadas polares
fig = px.line_polar(
    df, 
    r='Votos', 
    theta='Atributo', 
    color='Plataforma', 
    line_close=True, # Cierra el polígono
    title="Perfil del Consumidor: ¿Qué buscan los usuarios según su plataforma?",
    color_discrete_sequence=['#E50914', '#00C3FF', '#F47521'] # Colores de Netflix, Animeflv y Crunchyroll
)

# Rellenar el área de los polígonos para que parezca una infografía moderna
fig.update_traces(fill='toself', opacity=0.4)

# Ajustes de diseño limpio
fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 10]) # Rango de votos
    ),
    font=dict(size=14, family="Arial, sans-serif"),
    paper_bgcolor='white',
    plot_bgcolor='white',
    height=600,
    margin=dict(t=80, b=50, l=50, r=50)
)

fig.show()
