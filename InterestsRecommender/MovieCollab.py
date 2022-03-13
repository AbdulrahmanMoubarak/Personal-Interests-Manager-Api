import pandas as pd

# Read Data From Files and merge both files using the movieId
col_list = ["title", "movie_id"]
rating = pd.read_csv('Movies.csv', usecols=col_list)
df = pd.read_csv('Rating_Movies.csv').drop(['timestamp'], axis=1)

rating['movie_id'] = rating['movie_id'].astype(str)
df['movie_id'] = df['movie_id'].astype(str)

merged = pd.merge(df, rating)

# make table where the index is userId and coloums is Book title and the values are rating
user_rating = merged.pivot_table(index='userId', columns='title', values='rating')


# replace the Na values with 0
user_rating = user_rating.fillna(0)


# apply pearson rule for standaralization
movie_similarity = user_rating.corr(method='pearson')



# .dropna(thresh=0,axis=1)

# function for getting recommendation
def recommend_movie(movie_name, user_rating):
    if movie_name in movie_similarity:
        movie_score = movie_similarity[movie_name] * (user_rating - 2.5)
        movie_score = movie_score.sort_values(ascending=False)
        return movie_score

new_user = [('Rocky III', 5), ("Jumanji", 5), ("Father of the Bride Part II", 5)]

similar_movie = pd.DataFrame()
for movie, rating in new_user:
    similar_movie = similar_movie.append(recommend_movie(movie, rating), ignore_index=True)

#similar_movie.sum().sort_values(ascending=False)


print(similar_movie.sum().sort_values(ascending=False))