import pandas as pd

# Cargar los archivos CSV del dataset
movies = pd.read_csv('ml-latest-small/movies.csv')
ratings = pd.read_csv('ml-latest-small/ratings.csv')

# Mostrar las primeras 5 filas de cada archivo
print("Películas:")
print(movies.head())
print("\nCalificaciones:")
print(ratings.head())

# Mostrar información básica de los datasets
print("\nInformación de películas:")
print(movies.info())
print("\nInformación de calificaciones:")
print(ratings.info())


# Películas:
#    movieId                               title                                       genres
# 0        1                    Toy Story (1995)  Adventure|Animation|Children|Comedy|Fantasy
# 1        2                      Jumanji (1995)                   Adventure|Children|Fantasy
# 2        3             Grumpier Old Men (1995)                               Comedy|Romance
# 3        4            Waiting to Exhale (1995)                         Comedy|Drama|Romance
# 4        5  Father of the Bride Part II (1995)                                       Comedy

# Calificaciones:
#    userId  movieId  rating  timestamp
# 0       1        1     4.0  964982703
# 1       1        3     4.0  964981247
# 2       1        6     4.0  964982224
# 3       1       47     5.0  964983815
# 4       1       50     5.0  964982931

# Información de películas:
# <class 'pandas.core.frame.DataFrame'>
# RangeIndex: 9742 entries, 0 to 9741
# Data columns (total 3 columns):
 #   Column   Non-Null Count  Dtype 
# ---  ------   --------------  ----- 
#  0   movieId  9742 non-null   int64 
#  1   title    9742 non-null   object
#  2   genres   9742 non-null   object
# dtypes: int64(1), object(2)
# memory usage: 228.5+ KB
# None

# Información de calificaciones:
# <class 'pandas.core.frame.DataFrame'>
# RangeIndex: 100836 entries, 0 to 100835
# Data columns (total 4 columns):
 #   Column     Non-Null Count   Dtype  
# ---  ------     --------------   -----  
#  0   userId     100836 non-null  int64  
#  1   movieId    100836 non-null  int64  
#  2   rating     100836 non-null  float64
#  3   timestamp  100836 non-null  int64  
# dtypes: float64(1), int64(3)
# memory usage: 3.1 MB
# None


