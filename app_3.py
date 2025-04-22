import streamlit as st
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc

# Configurar la página al inicio
st.set_page_config(page_title="Recomendador de Películas", page_icon="🎥")

# Cargar los archivos CSV del dataset
@st.cache_data
def load_data():
    movies = pd.read_csv('ml-latest-small/movies.csv')
    ratings = pd.read_csv('ml-latest-small/ratings.csv')
    user_movie_matrix = ratings.pivot(index='userId', columns='movieId', values='rating')
    movie_correlation = user_movie_matrix.corr(method='pearson', min_periods=30)
    return movies, user_movie_matrix, movie_correlation

movies, user_movie_matrix, movie_correlation = load_data()

# Función para calcular un índice de género
def calculate_genre_index(movie_genres, recommended_genres):
    movie_genres_set = set(movie_genres)
    recommended_genres_set = set(recommended_genres)
    common_genres = len(movie_genres_set.intersection(recommended_genres_set))
    total_genres = len(movie_genres_set.union(recommended_genres_set))
    return common_genres / total_genres if total_genres > 0 else 0

# Función para obtener recomendaciones
def get_movie_recommendations(movie_id, movie_title_exact, num_recommendations=5, min_common_users=50):
    movie_genres = movies[movies['movieId'] == movie_id]['genres'].iloc[0].split('|')
    
    genre_priority_map = {
        'Action': ['Action', 'Adventure', 'Thriller'],
        'Thriller': ['Thriller', 'Action', 'Crime'],
        'Adventure': ['Adventure', 'Action', 'Fantasy'],
        'Fantasy': ['Fantasy', 'Adventure', 'Children'],
        'Children': ['Children', 'Fantasy', 'Animation'],
        'Animation': ['Animation', 'Children', 'Comedy'],
        'Comedy': ['Comedy', 'Romance', 'Drama'],
        'Romance': ['Romance', 'Drama', 'Comedy'],
        'Drama': ['Drama', 'Romance', 'Crime'],
        'Horror': ['Horror', 'Thriller', 'Mystery'],
        'Sci-Fi': ['Sci-Fi', 'Action', 'Adventure'],
        'Crime': ['Crime', 'Thriller', 'Drama']
    }
    
    priority_genres = []
    for genre in movie_genres:
        if genre in genre_priority_map:
            priority_genres = genre_priority_map[genre]
            break
    if not priority_genres:
        priority_genres = movie_genres
    
    if 'Jumanji' in movie_title_exact:
        priority_genres = ['Children', 'Fantasy']
    
    default_min_common_users = 30 if 'Horror' in movie_genres or 'Mystery' in movie_genres else 50  # Reducido de 60 a 50
    min_common_users = min(min_common_users, default_min_common_users)
    
    relevant_genres = [g for g in movie_genres if g in priority_genres] or movie_genres
    
    similar_movies = movie_correlation[movie_id].dropna().sort_values(ascending=False)
    similar_movies = similar_movies[similar_movies.index != movie_id]
    
    recommendations = movies[movies['movieId'].isin(similar_movies.index)].copy()
    recommendations['correlation'] = similar_movies[recommendations['movieId']].values
    
    recommendations = recommendations[
        recommendations['genres'].apply(
            lambda x: any(genre in x.split('|') for genre in relevant_genres)
        )
    ]
    
    if recommendations.empty:
        return None, f"No encontramos películas similares con géneros en común para '{movie_title_exact}'. Prueba con otra película o ajusta los parámetros.", movie_genres, relevant_genres
    
    common_users = []
    valid_movie_ids = []
    for similar_movie_id in recommendations['movieId']:
        common_ratings = user_movie_matrix[[movie_id, similar_movie_id]].dropna()
        num_common = len(common_ratings)
        if num_common >= min_common_users:
            common_users.append(num_common)
            valid_movie_ids.append(similar_movie_id)
    
    recommendations = recommendations[recommendations['movieId'].isin(valid_movie_ids)].copy()
    recommendations['correlation'] = recommendations['correlation'].round(3)
    recommendations['common_users'] = common_users
    
    if len(recommendations) < num_recommendations:
        recommendations = movies[movies['movieId'].isin(similar_movies.index)].copy()
        recommendations['correlation'] = similar_movies[recommendations['movieId']].values
        common_users = []
        valid_movie_ids = []
        for similar_movie_id in recommendations['movieId']:
            common_ratings = user_movie_matrix[[movie_id, similar_movie_id]].dropna()
            num_common = len(common_ratings)
            if num_common >= min_common_users:
                common_users.append(num_common)
                valid_movie_ids.append(similar_movie_id)
        recommendations = recommendations[recommendations['movieId'].isin(valid_movie_ids)].copy()
        recommendations['correlation'] = recommendations['correlation'].round(3)
        recommendations['common_users'] = common_users
        if len(recommendations) < num_recommendations:
            return None, f"Solo encontramos {len(recommendations)} películas similares para '{movie_title_exact}' (se requieren al menos {min_common_users} usuarios en común). Intenta reducir el número de recomendaciones o el umbral de usuarios en común.", movie_genres, relevant_genres
    
    # Calcular índice de género para cada recomendación
    recommendations['genre_index'] = recommendations['genres'].apply(
        lambda x: calculate_genre_index(movie_genres, x.split('|'))
    )
    
    recommendations = recommendations.sort_values(by='correlation', ascending=False).head(num_recommendations)
    return recommendations[['title', 'genres', 'correlation', 'common_users', 'genre_index']], None, movie_genres, relevant_genres

# Interfaz de Streamlit
st.title("🎥 Sistema de Recomendación de Películas de Pol Monsalvo")
st.markdown("""
¡Bienvenido! Esta aplicación te permite encontrar recomendaciones de películas basadas en similitudes de calificaciones y géneros.  
Ingresa un título (por ejemplo, "Toy Story" o "Jumanji") y selecciona una película para ver recomendaciones personalizadas.
""")

# Campo de búsqueda y selección de título
movie_title = st.text_input("Título de la película:", value="Toy Story")
matches = movies[movies['title'].str.contains(movie_title, case=False, na=False)]['title'].tolist()

if not matches:
    st.error(f"No se encontraron películas que coincidan con '{movie_title}'. Intenta con otro título.")
    selected_movie = None
else:
    selected_movie = st.selectbox("Selecciona una película:", matches)

num_recommendations = st.slider("Número de recomendaciones:", 1, 10, 5)
min_common_users = st.slider("Mínimo de usuarios en común:", 10, 100, 50)  # Ajustado a 50

if st.button("Obtener recomendaciones") and selected_movie:
    movie_id = movies[movies['title'] == selected_movie]['movieId'].iloc[0]
    recommendations, error, movie_genres, relevant_genres = get_movie_recommendations(movie_id, selected_movie, num_recommendations, min_common_users)
    
    if recommendations is None:
        st.warning(error)
    else:
        # Mostrar información de la película seleccionada
        selected_movie_row = movies[movies['title'] == selected_movie]
        st.write(f"**Película seleccionada**: {selected_movie}")
        st.write(f"**Géneros**: {', '.join(movie_genres)}")
        st.write(f"**Géneros prioritarios usados**: {', '.join(relevant_genres)}")
        st.write("**Recomendaciones**:")
        st.dataframe(recommendations[['title', 'genres', 'correlation', 'common_users']], use_container_width=True)
        
        # Gráfico de dispersión 3D
        st.subheader("Visualización 3D de Recomendaciones")
        fig_3d = px.scatter_3d(
            recommendations,
            x='correlation',
            y='common_users',
            z='genre_index',
            text='title',
            color='correlation',
            size='common_users',
            size_max=50,  # Aumentar el tamaño máximo de los puntos
            opacity=0.7,
            title="Relación entre Correlación, Usuarios en Común e Índice de Género",
            labels={
                'correlation': 'Correlación',
                'common_users': 'Usuarios en Común',
                'genre_index': 'Índice de Género'
            },
            color_continuous_scale='Rainbow'
        )
        fig_3d.update_traces(textposition='top center')
        fig_3d.update_layout(scene=dict(
            xaxis_title='Correlación',
            yaxis_title='Usuarios en Común',
            zaxis_title='Índice de Género'
        ))
        st.plotly_chart(fig_3d, use_container_width=True)
        
        # Gráfico de red interactivo
        st.subheader("Red de Relaciones entre Películas")
        # Crear nodos y enlaces
        nodes = [selected_movie] + recommendations['title'].tolist()
        edges = [(selected_movie, row['title'], row['correlation']) for _, row in recommendations.iterrows()]
        
        # Crear un diccionario para mapear títulos a correlaciones
        correlation_map = {selected_movie: 1.0}  # La película seleccionada tiene correlación 1
        for edge in edges:
            correlation_map[edge[1]] = edge[2]  # Título de la recomendación -> correlación
        
        # Normalizar correlaciones para mapear a colores (entre 0 y 1)
        correlations = [edge[2] for edge in edges]
        min_corr = min(correlations) if correlations else 0
        max_corr = max(correlations) if correlations else 1
        norm_correlations = [(corr - min_corr) / (max_corr - min_corr) if max_corr != min_corr else 0.5 for corr in correlations]
        
        # Mapear correlaciones normalizadas a colores usando la escala Viridis
        viridis_colors = pc.sequential.Viridis
        edge_colors = [viridis_colors[int(norm_corr * (len(viridis_colors) - 1))] for norm_corr in norm_correlations]
        
        # Crear trazas de líneas individuales
        edge_traces = []
        for i, edge in enumerate(edges):
            x0, x1 = 0, 1
            y0, y1 = nodes.index(edge[0]), nodes.index(edge[1])
            edge_trace = go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                line=dict(width=4, color=edge_colors[i]),  # Aumentar el grosor de las líneas
                hoverinfo='none',
                mode='lines'
            )
            edge_traces.append(edge_trace)
        
        # Crear nodos
        node_x = [0 if node == selected_movie else 1 for node in nodes]
        node_y = [i for i in range(len(nodes))]
        textpositions = ['middle right' if node == selected_movie else 'middle left' for node in nodes]
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=nodes,
            textposition=textpositions,
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='Rainbow',
                size=20,  # Aumentar el tamaño de los nodos
                color=[correlation_map[node] for node in nodes],
                colorbar=dict(title='Correlación'),
                line_width=2
            )
        )
        
        fig_network = go.Figure(data=edge_traces + [node_trace],
                                layout=go.Layout(
                                    title='Red de Películas Similares',
                                    showlegend=False,
                                    hovermode='closest',
                                    margin=dict(b=20, l=5, r=5, t=40),
                                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                                ))
        st.plotly_chart(fig_network, use_container_width=True)