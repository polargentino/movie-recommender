import pandas as pd

# Cargar los archivos CSV del dataset
movies = pd.read_csv('ml-latest-small/movies.csv')
ratings = pd.read_csv('ml-latest-small/ratings.csv')

# Crear la matriz de usuarios-películas
user_movie_matrix = ratings.pivot(index='userId', columns='movieId', values='rating')

# Calcular la matriz de correlación entre películas
movie_correlation = user_movie_matrix.corr(method='pearson', min_periods=30)

# Función para obtener recomendaciones
def get_movie_recommendations(movie_title, num_recommendations=5):
    # Buscar el movieId y géneros de la película dada (coincidencia exacta)
    movie_match = movies[movies['title'] == movie_title]
    if movie_match.empty:
        return f"No se encontró la película '{movie_title}'. Intenta con otro título."
    
    movie_id = movie_match['movieId'].iloc[0]
    movie_genres = movie_match['genres'].iloc[0].split('|')
    
    # Obtener las correlaciones para esa película
    similar_movies = movie_correlation[movie_id].dropna().sort_values(ascending=False)
    
    # Excluir la película misma
    similar_movies = similar_movies[similar_movies.index != movie_id]
    
    # Filtrar por géneros: solo películas que compartan al menos un género
    recommendations = movies[movies['movieId'].isin(similar_movies.index)].copy()
    recommendations['correlation'] = similar_movies[recommendations['movieId']].values
    
    # Filtrar películas con géneros en común
    recommendations = recommendations[
        recommendations['genres'].apply(
            lambda x: any(genre in x.split('|') for genre in movie_genres)
        )
    ]
    
    # Verificar si hay suficientes recomendaciones
    if len(recommendations) < num_recommendations:
        return f"No hay suficientes películas similares con géneros en común para '{movie_title}'. Encontradas: {len(recommendations)}."
    
    # Tomar las primeras num_recommendations
    recommendations = recommendations.head(num_recommendations)
    
    # Calcular el número de usuarios en común para cada película
    common_users = []
    for similar_movie_id in recommendations['movieId']:
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
#                   title  ... common_users
# 0      Toy Story (1995)  ...           68
# 9      GoldenEye (1995)  ...           56
# 32          Babe (1995)  ...           56
# 44    Pocahontas (1995)  ...           37
# 84  Broken Arrow (1996)  ...           33

# [5 rows x 4 columns]