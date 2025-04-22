import pandas as pd

# Cargar los archivos CSV del dataset
movies = pd.read_csv('ml-latest-small/movies.csv')
ratings = pd.read_csv('ml-latest-small/ratings.csv')

# Crear la matriz de usuarios-películas
user_movie_matrix = ratings.pivot(index='userId', columns='movieId', values='rating')

# Calcular la matriz de correlación entre películas
movie_correlation = user_movie_matrix.corr(method='pearson', min_periods=30)

# Función para obtener recomendaciones
def get_movie_recommendations(movie_title, num_recommendations=5, min_common_users=50):
    # Buscar el movieId y géneros de la película dada (búsqueda parcial)
    movie_match = movies[movies['title'].str.contains(movie_title, case=False, na=False)]
    if movie_match.empty:
        return f"No se encontró la película '{movie_title}'. Intenta con otro título."
    
    # Si hay múltiples coincidencias, tomar la primera
    movie_id = movie_match['movieId'].iloc[0]
    movie_title_exact = movie_match['title'].iloc[0]
    movie_genres = movie_match['genres'].iloc[0].split('|')
    
    # Definir géneros prioritarios
    priority_genres = ['Animation', 'Children', 'Fantasy', 'Adventure']
    relevant_genres = [g for g in movie_genres if g in priority_genres] or movie_genres
    
    # Mostrar los géneros de la película ingresada
    print(f"Géneros de '{movie_title_exact}': {', '.join(movie_genres)}")
    print(f"Géneros prioritarios usados: {', '.join(relevant_genres)}")
    
    # Obtener las correlaciones para esa película
    similar_movies = movie_correlation[movie_id].dropna().sort_values(ascending=False)
    
    # Excluir la película misma
    similar_movies = similar_movies[similar_movies.index != movie_id]
    
    # Filtrar por géneros y usuarios en común
    recommendations = movies[movies['movieId'].isin(similar_movies.index)].copy()
    recommendations['correlation'] = similar_movies[recommendations['movieId']].values
    
    # Filtrar películas con géneros prioritarios en común
    recommendations = recommendations[
        recommendations['genres'].apply(
            lambda x: any(genre in x.split('|') for genre in relevant_genres)
        )
    ]
    
    # Calcular usuarios en común y filtrar por min_common_users
    common_users = []
    valid_movie_ids = []
    for similar_movie_id in recommendations['movieId']:
        common_ratings = user_movie_matrix[[movie_id, similar_movie_id]].dropna()
        num_common = len(common_ratings)
        if num_common >= min_common_users:
            common_users.append(num_common)
            valid_movie_ids.append(similar_movie_id)
    
    # Filtrar recomendaciones por movieId válidos
    recommendations = recommendations[recommendations['movieId'].isin(valid_movie_ids)].copy()
    recommendations['common_users'] = common_users
    
    # Verificar si hay suficientes recomendaciones
    if len(recommendations) < num_recommendations:
        return f"No hay suficientes películas similares con géneros en común y al menos {min_common_users} usuarios en común para '{movie_title_exact}'. Encontradas: {len(recommendations)}."
    
    # Ordenar por correlación y tomar las primeras num_recommendations
    recommendations = recommendations.sort_values(by='correlation', ascending=False).head(num_recommendations)
    
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