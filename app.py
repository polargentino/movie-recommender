import streamlit as st
import pandas as pd

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
def get_movie_recommendations(movie_title, num_recommendations=5, min_common_users=50):
    movie_match = movies[movies['title'].str.contains(movie_title, case=False, na=False)]
    if movie_match.empty:
        return None, f"No se encontró la película '{movie_title}'. Intenta con otro título."
    
    movie_id = movie_match['movieId'].iloc[0]
    movie_title_exact = movie_match['title'].iloc[0]
    movie_genres = movie_match['genres'].iloc[0].split('|')
    
    priority_genres = ['Animation', 'Children', 'Fantasy', 'Adventure']
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
    
    common_users = []
    valid_movie_ids = []
    for similar_movie_id in recommendations['movieId']:
        common_ratings = user_movie_matrix[[movie_id, similar_movie_id]].dropna()
        num_common = len(common_ratings)
        if num_common >= min_common_users:
            common_users.append(num_common)
            valid_movie_ids.append(similar_movie_id)
    
    recommendations = recommendations[recommendations['movieId'].isin(valid_movie_ids)].copy()
    recommendations['common_users'] = common_users
    
    if len(recommendations) < num_recommendations:
        return None, f"No hay suficientes películas similares con géneros en común y al menos {min_common_users} usuarios en común para '{movie_title_exact}'. Encontradas: {len(recommendations)}."
    
    recommendations = recommendations.sort_values(by='correlation', ascending=False).head(num_recommendations)
    return recommendations[['title', 'genres', 'correlation', 'common_users']], movie_title_exact, movie_genres, relevant_genres

# Interfaz de Streamlit
st.title("Sistema de Recomendación de Películas de Pol Monsalvo")
st.write("Ingresa el nombre de una película para obtener recomendaciones basadas en similitud de calificaciones y géneros.")

movie_title = st.text_input("Título de la película:", value="Toy Story")
num_recommendations = st.slider("Número de recomendaciones:", 1, 10, 5)

if st.button("Obtener recomendaciones"):
    recommendations, *info = get_movie_recommendations(movie_title, num_recommendations)
    if recommendations is None:
        st.error(info)
    else:
        movie_title_exact, movie_genres, relevant_genres = info
        st.write(f"**Película seleccionada**: {movie_title_exact}")
        st.write(f"**Géneros**: {', '.join(movie_genres)}")
        st.write(f"**Géneros prioritarios usados**: {', '.join(relevant_genres)}")
        st.write("**Recomendaciones**:")
        st.dataframe(recommendations)


#         ┌──(env)─(pol㉿kali)-[~/Desktop/movie-recommender]
# └─$ streamlit run app.py

#       👋 Welcome to Streamlit!

#       If you’d like to receive helpful onboarding emails, news, offers, promotions,
#       and the occasional swag, please enter your email address below. Otherwise,
#       leave this field blank.

#       Email:  

#   You can find our privacy policy at https://streamlit.io/privacy-policy

#   Summary:
#   - This open source library collects usage statistics.
#   - We cannot see and do not store information contained inside Streamlit apps,
#     such as text, charts, images, etc.
#   - Telemetry data is stored in servers in the United States.
#   - If you'd like to opt out, add the following to ~/.streamlit/config.toml,
#     creating that file if necessary:

#     [browser]
#     gatherUsageStats = false


#   You can now view your Streamlit app in your browser.

#   Local URL: http://localhost:8501
#   Network URL: http://192.168.1.14:8501

# ^C  Stopping...
        