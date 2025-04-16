import pandas as pd

# Cargar los archivos CSV del dataset
movies = pd.read_csv('ml-latest-small/movies.csv')
ratings = pd.read_csv('ml-latest-small/ratings.csv')

# Crear la matriz de usuarios-películas
user_movie_matrix = ratings.pivot(index='userId', columns='movieId', values='rating')

# Mostrar las primeras 5 filas de la matriz
print("Matriz de usuarios-películas (primeras 5 filas):")
print(user_movie_matrix.head())

# Mostrar el tamaño de la matriz
print("\nTamaño de la matriz (usuarios x películas):", user_movie_matrix.shape)


# Matriz de usuarios-películas (primeras 5 filas):
# movieId  1       2       3       4       ...  193583  193585  193587  193609
# userId                                   ...                                
# 1           4.0     NaN     4.0     NaN  ...     NaN     NaN     NaN     NaN
# 2           NaN     NaN     NaN     NaN  ...     NaN     NaN     NaN     NaN
# 3           NaN     NaN     NaN     NaN  ...     NaN     NaN     NaN     NaN
# 4           NaN     NaN     NaN     NaN  ...     NaN     NaN     NaN     NaN
# 5           4.0     NaN     NaN     NaN  ...     NaN     NaN     NaN     NaN

# [5 rows x 9724 columns]

# Tamaño de la matriz (usuarios x películas): (610, 9724)
