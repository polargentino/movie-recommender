import pandas as pd

# Cargar los archivos CSV del dataset
movies = pd.read_csv('ml-latest-small/movies.csv')
ratings = pd.read_csv('ml-latest-small/ratings.csv')

# Crear la matriz de usuarios-películas
user_movie_matrix = ratings.pivot(index='userId', columns='movieId', values='rating')

# Calcular la matriz de correlación entre películas
movie_correlation = user_movie_matrix.corr(method='pearson', min_periods=20)

# Función para obtener recomendaciones
def get_movie_recommendations(movie_title, num_recommendations=5):
    # Buscar el movieId de la película dada (coincidencia exacta)
    movie_match = movies[movies['title'] == movie_title]
    if movie_match.empty:
        return f"No se encontró la película '{movie_title}'. Intenta con otro título."
    
    movie_id = movie_match['movieId'].iloc[0]
    
    # Obtener las correlaciones para esa película
    similar_movies = movie_correlation[movie_id].dropna().sort_values(ascending=False)
    
    # Excluir la película misma
    similar_movies = similar_movies[similar_movies.index != movie_id]
    
    # Obtener los títulos de las películas recomendadas
    recommendations = movies[movies['movieId'].isin(similar_movies.index[:num_recommendations])].copy()
    recommendations.loc[:, 'correlation'] = similar_movies[:num_recommendations].values
    
    return recommendations[['title', 'genres', 'correlation']]

# Ejemplo: Recomendar películas similares a "Toy Story (1995)"
print("Recomendaciones para 'Toy Story (1995)':")
print(get_movie_recommendations('Toy Story (1995)', 5))

# Recomendaciones para 'Toy Story (1995)':
#                         title  ... correlation
# 2027     Arachnophobia (1990)  ...    0.699211
# 2355       Toy Story 2 (1999)  ...    0.674658
# 5374  Incredibles, The (2004)  ...    0.663129
# 7906             Brave (2012)  ...    0.652424
# 8151        Iron Man 3 (2013)  ...    0.643301

# [5 rows x 3 columns]