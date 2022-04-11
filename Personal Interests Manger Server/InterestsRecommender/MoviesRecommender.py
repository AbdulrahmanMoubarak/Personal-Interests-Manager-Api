import pandas as pd
import scipy
import threadpoolctl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import sqlite3

conn = sqlite3.connect("pim_database.db")

class Movie:

    def ContentWithUserId(self,userId):
        df = pd.read_sql_query("""Select genres,movie_id from movies_metadata""", conn)
        df2 = pd.read_sql_query("""Select movie_id from movie_rating where user_id=""" + str(userId), conn)
        merged = pd.merge(df, df2)
        for movie_id in merged['movie_id'].values:
            self.Contentbased(movie_id, df)

    def CollabWithUserId(self, userId):
        df = pd.read_sql_query("""Select movie_id , title from movies_metadata""", conn)
        df2 = pd.read_sql_query("""Select movie_id,rating from movie_rating where user_id=""" + str(userId), conn)
        df3 = pd.read_sql_query("""Select user_id,movie_id,rating from movie_rating""", conn)
        df['movie_id'] = df['movie_id'].astype(str)
        df2['movie_id'] = df2['movie_id'].astype(str)
        df3['movie_id'] = df3['movie_id'].astype(str)
        merged = pd.merge(df, df2)
        merged2 = pd.merge(df, df3)
        self.CollabBased(merged,merged2)

    def Contentbased(self,movieid, df):
        id = movieid
        ind = df[df['movie_id'] == id].index.values[0]
        row_genre = df.at[ind, 'genres']
        temp = pd.Series()

        # 1246
        result = None
        for chunk in pd.read_sql_query("""Select genres,movie_id from movies_metadata""", conn, chunksize=7000):
            # chunk_result = voters_street.value_counts()
            chunk = chunk.reset_index()
            if not id in chunk["movie_id"].unique():
                df2 = {'genres': row_genre, 'movie_id': id}
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
            indices = pd.Series(chunk.index, index=chunk['movie_id']).drop_duplicates()

            # Function that takes in movie title as input and outputs most similar movies
            temp=temp.append(self.__recommd(id,cosine_sim,indices,chunk))
        print(temp.to_frame())

    def __recommd(self,title,cosine_sim,indices,chunk):

        # Get the index of the movie that matches the title
        idx = indices[title]

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True, )

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:11]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        v=chunk['movie_id'].iloc[movie_indices]
        # Return the top 10 most similar movies
        return v

    def CollabBased(self,merged,merged2):
        # make table where the index is userId and coloums is Book title and the values are rating
        user_rating = merged2.pivot_table(index='user_id', columns='movie_id', values='rating')

        # replace the Na values with 0
        user_rating = user_rating.fillna(0)

        # apply pearson rule for standaralization
        movie_similarity = user_rating.corr(method='pearson')

        # function for getting recommendation
        def recommend_movie(movie_id, user_rating):
            if movie_id in movie_similarity:
                movie_score = movie_similarity[movie_id] * (user_rating - 2.5)
                movie_score = movie_score.sort_values(ascending=False)
                return movie_score

        similar_movie = pd.DataFrame()

        for index, row in merged.iterrows():
            similar_movie = similar_movie.append(recommend_movie(row["movie_id"], row["rating"]), ignore_index=True)

        # similar_movie.sum().sort_values(ascending=False)

        print(similar_movie.sum().sort_values(ascending=False))

r=Movie()
r.ContentWithUserId(46)
