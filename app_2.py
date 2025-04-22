import streamlit as st
import pandas as pd

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

# Función para obtener recomendaciones
def get_movie_recommendations(movie_id, movie_title_exact, num_recommendations=5, min_common_users=60):
    movie_genres = movies[movies['movieId'] == movie_id]['genres'].iloc[0].split('|')
    
    # Ajustar géneros prioritarios según los géneros de la película
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
    
    # Seleccionar los géneros prioritarios basados en el primer género relevante de la película
    priority_genres = []
    for genre in movie_genres:
        if genre in genre_priority_map:
            priority_genres = genre_priority_map[genre]
            break
    if not priority_genres:
        priority_genres = movie_genres  # Si no hay coincidencia, usar todos los géneros de la película
    
    # Ajuste especial para Jumanji
    if 'Jumanji' in movie_title_exact:
        priority_genres = ['Children', 'Fantasy']
    
    # Ajuste para géneros menos comunes (como Horror)
    default_min_common_users = 30 if 'Horror' in movie_genres or 'Mystery' in movie_genres else 60
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
    
    # Verificar si hay recomendaciones después del filtro de géneros
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
    
    # Si no hay suficientes recomendaciones, relajar el filtro de géneros
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
    
    recommendations = recommendations.sort_values(by='correlation', ascending=False).head(num_recommendations)
    return recommendations[['title', 'genres', 'correlation', 'common_users']], None, movie_genres, relevant_genres

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
min_common_users = st.slider("Mínimo de usuarios en común:", 10, 100, 60)

if st.button("Obtener recomendaciones") and selected_movie:
    movie_id = movies[movies['title'] == selected_movie]['movieId'].iloc[0]
    recommendations, error, movie_genres, relevant_genres = get_movie_recommendations(movie_id, selected_movie, num_recommendations, min_common_users)
    
    if recommendations is None:
        st.warning(error)
    else:
        st.write(f"**Película seleccionada**: {selected_movie}")
        st.write(f"**Géneros**: {', '.join(movie_genres)}")
        st.write(f"**Géneros prioritarios usados**: {', '.join(relevant_genres)}")
        st.write("**Recomendaciones**:")
        st.dataframe(recommendations, use_container_width=True)