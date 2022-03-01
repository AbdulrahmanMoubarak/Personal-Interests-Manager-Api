import pandas as pd
import scipy
import threadpoolctl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def contentBased(movie_name):
    col_list = ["genres", "title"]
    df = pd.read_csv("Movies.csv", usecols=col_list)

    name = movie_name
    ind = df[df['title'] == name].index.values[0]
    row_genre = df.at[ind, 'genres']

    mylist=[]

    result = None
    for chunk in pd.read_csv("Movies.csv", usecols=col_list, chunksize=7000):
        # chunk_result = voters_street.value_counts()

        if not name in chunk.values:
            df2 = {'genres': row_genre, 'title': name}
            chunk = chunk.append(df2, ignore_index=True)

        chunk['genres'] = chunk['genres'].astype(str)
        tfidf = TfidfVectorizer(stop_words='english')

        # Replace NaN with an empty string
        chunk['genres'] = chunk['genres'].fillna('')

        # Construct the required TF-IDF matrix by fitting and transforming the data
        tfidf_matrix = tfidf.fit_transform(chunk['genres'])

        # Output the shape of tfidf_matrix
        # tfidf_matrix.shape

        # Compute the cosine similarity matrix
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        # Construct a reverse map of indices and movie titles
        indices = pd.Series(chunk.index, index=chunk['title']).drop_duplicates()

        # Function that takes in movie title as input and outputs most similar movies
        def get_recommendations(title, cosine_sim=cosine_sim):
            # Get the index of the movie that matches the title
            idx = indices[title]

            # Get the pairwsie similarity scores of all movies with that movie
            sim_scores = list(enumerate(cosine_sim[idx]))

            # Sort the movies based on the similarity scores
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True, )

            # Get the scores of the 10 most similar movies
            sim_scores = sim_scores[1:5]

            # Get the movie indices
            movie_indices = [i[0] for i in sim_scores]

            # Return the top 10 most similar movies
            return chunk['title'].iloc[movie_indices]
        mydf = get_recommendations(movie_name)

        mylist.append(mydf.values.tolist())

    return mylist


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

new_user = [ ("Jumanji", 5), ("Father of the Bride Part II", 5)]

similar_movie = pd.DataFrame()
for movie, rating in new_user:
    similar_movie = similar_movie.append(recommend_movie(movie, rating), ignore_index=True)

if similar_movie.size == 0:
    for movie, rating in new_user:
        print(movie)
        print(contentBased(movie))