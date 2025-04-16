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
    
    # Verificar si hay suficientes recomendaciones
    if len(similar_movies) < num_recommendations:
        return f"No hay suficientes películas similares para '{movie_title}'. Encontradas: {len(similar_movies)}."
    
    # Obtener los títulos de las películas recomendadas
    recommendations = movies[movies['movieId'].isin(similar_movies.index[:num_recommendations])].copy()
    recommendations.loc[:, 'correlation'] = similar_movies[:num_recommendations].values
    
    # Calcular el número de usuarios en común para cada película
    common_users = []
    for similar_movie_id in similar_movies.index[:num_recommendations]:
        common_ratings = user_movie_matrix[[movie_id, similar_movie_id]].dropna()
        common_users.append(len(common_ratings))
    recommendations.loc[:, 'common_users'] = common_users
    
    return recommendations[['title', 'genres', 'correlation', 'common_users']]

# Bucle interactivo para ingresar títulos
while True:
    input_movie_title = input("Ingresa el título de una película (o 'salir' para terminar): ")
    if input_movie_title.lower() == 'salir':
        print("¡Programa terminado!")
        break
    
    print(f"\nRecomendaciones para '{input_movie_title}':")
    result = get_movie_recommendations(input_movie_title, 5)
    print(result)
    print()

# Ingresa el título de una película (o 'salir' para terminar): Jumanji (1995)

# Recomendaciones para 'Jumanji (1995)':
#                             title  ... common_users
# 140           First Knight (1995)  ...           21
# 1135             Liar Liar (1997)  ...           24
# 2920   Remember the Titans (2000)  ...           22
# 3461           Others, The (2001)  ...           20
# 4851  The Butterfly Effect (2004)  ...           36

# [5 rows x 4 columns]