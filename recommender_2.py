import pandas as pd

# Cargar los archivos CSV del dataset
movies = pd.read_csv('ml-latest-small/movies.csv')
ratings = pd.read_csv('ml-latest-small/ratings.csv')

# Crear la matriz de usuarios-películas
user_movie_matrix = ratings.pivot(index='userId', columns='movieId', values='rating')

# Calcular la matriz de correlación entre películas
movie_correlation = user_movie_matrix.corr(method='pearson', min_periods=10)

# Función para obtener recomendaciones
def get_movie_recommendations(movie_title, num_recommendations=5):
    # Encontrar el movieId de la película dada
    movie_id = movies[movies['title'].str.contains(movie_title, case=False)]['movieId'].iloc[0]
    
    # Obtener las correlaciones para esa película
    similar_movies = movie_correlation[movie_id].dropna().sort_values(ascending=False)
    
    # Excluir la película misma
    similar_movies = similar_movies[similar_movies.index != movie_id]
    
    # Obtener los títulos de las películas recomendadas
    recommendations = movies[movies['movieId'].isin(similar_movies.index[:num_recommendations])]
    recommendations['correlation'] = similar_movies[:num_recommendations].values
    
    return recommendations[['title', 'genres', 'correlation']]

# Ejemplo: Recomendar películas similares a "Toy Story"
print("Recomendaciones para 'Toy Story':")
print(get_movie_recommendations('Toy Story', 5))

# Recomendaciones para 'Toy Story':
# /home/pol/Desktop/movie-recommender/recommender_2.py:26: SettingWithCopyWarning: 
# A value is trying to be set on a copy of a slice from a DataFrame.
# Try using .loc[row_indexer,col_indexer] = value instead

# See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
#   recommendations['correlation'] = similar_movies[:num_recommendations].values
#                                                   title  ... correlation
# 4308                              Mighty Wind, A (2003)  ...    0.913282
# 6586                     Darjeeling Limited, The (2007)  ...    0.898497
# 6827  Let the Right One In (Låt den rätte komma in) ...  ...    0.868810
# 8449                              22 Jump Street (2014)  ...    0.857624
# 8699                  Untitled Spider-Man Reboot (2017)  ...    0.832835

# [5 rows x 3 columns]
