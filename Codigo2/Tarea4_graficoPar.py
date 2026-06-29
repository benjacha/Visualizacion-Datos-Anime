import pandas as pd
import plotly.graph_objects as go

def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    """Carga y limpia el dataset, filtrando solo series tipo TV."""
    df = pd.read_csv(csv_path)
    
    # 1. Definimos las columnas necesarias incluyendo 'type'
    required_columns = ['title', 'score', 'episodes', 'aired_string', 'popularity', 'type']
    
    # 2. Nos aseguramos de mantener solo esas columnas
    df = df[required_columns].copy()
    
    # 3. Filtramos por tipo 'TV' primero
    df = df[df['type'] == 'TV'].copy()
    
    # 4. Ahora sí, eliminamos nulos
    df.dropna(subset=required_columns, inplace=True)

    # 5. Limpieza de datos (conversión a numéricos)
    df['episodes'] = pd.to_numeric(df['episodes'], errors='coerce')
    df = df[df['episodes'] > 0].dropna()

    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    df = df[df['score'] > 0].dropna()
    
    df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')

    # 6. Extraer año
    df['year'] = df['aired_string'].str.extract(r'(\d{4})')[0].astype(float)
    df.dropna(subset=['year'], inplace=True)
    df['year'] = df['year'].astype(int)

    return df

def create_parallel_coords_figure(dataframe: pd.DataFrame, title: str, max_episodes: int) -> go.Figure:
    # Ordenar por score para que los mejores puntajes queden arriba
    df_sorted = dataframe.sort_values(by='score', ascending=True)

    fig = go.Figure(data=go.Parcoords(
        line=dict(
            color=df_sorted['score'],
            
            colorscale=[
                [0.0, 'rgba(200, 0, 0, 0.4)'],   # Rojo Intenso
                [0.5, 'rgba(220, 220, 0, 0.3)'], # Amarillo
                [1.0, 'rgba(0, 160, 0, 0.4)']    # Verde Fuerte
            ],
            showscale=True,
            cmin=2.0,
            cmax=10.0
        ),
        dimensions=[
            dict(range=[df_sorted['year'].min(), df_sorted['year'].max()], label='Año', values=df_sorted['year']),
            dict(range=[0, max_episodes], label='Episodios', values=df_sorted['episodes']),
            dict(range=[df_sorted['popularity'].max(), 1], label='Popularidad (Ranking)', values=df_sorted['popularity']),
            dict(range=[2.0, 10.0], label='Score', values=df_sorted['score'], tickvals=[2, 4, 6, 8, 10])
        ]
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(color='#FFFFFF', size=18)),
        height=800,
        plot_bgcolor='#1A1A24',
        paper_bgcolor='#1A1A24',
        font=dict(color='#FFFFFF', family='Arial', size=12),
        margin=dict(l=60, r=60, b=80, t=100)
    )
    return fig

def main() -> None:
    csv_path = 'AnimeList.csv'
    df = load_and_clean_data(csv_path)

    # Segmentación
    df_short = df[df['episodes'] <= 60].copy()
    df_long = df[df['episodes'] > 60].copy()

    df_short = df_short.sort_values(by='score', ascending=True)
    df_long = df_long.sort_values(by='score', ascending=True)
    fig_short = create_parallel_coords_figure(df_short, 'Perfil de Éxito - Formato Corto', 60)
    fig_long = create_parallel_coords_figure(df_long, 'Perfil de Éxito - Formato Longevo', int(df_long['episodes'].max()))

    fig_short.show()
    fig_long.show()

if __name__ == '__main__':
    main()
