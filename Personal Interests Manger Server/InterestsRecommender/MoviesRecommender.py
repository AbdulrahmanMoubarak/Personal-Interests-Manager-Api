import pandas as pd
import scipy
import threadpoolctl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import sqlite3
from random import shuffle


class MovieRecommender:
    def ContentWithMovieId(self, MovieId, conn, numMovies):

        exists = conn.cursor().execute('''SELECT * FROM movies_metadata WHERE movie_id = (?)''', [MovieId]).fetchall()
        if len(exists) == 0:
            return []

        df = pd.read_sql_query("""Select genres,movie_id from movies_metadata""", conn)
        pp = pd.Series()
        pp = pp.append(self.Contentbased(MovieId, df, conn, numMovies))
        return self.__extractRecommendationFromContentDataFrame(pp)

    def CollabWithMovieId(self, userId, movieId, conn):
        userRating = conn.cursor().execute('''SELECT * FROM movie_rating WHERE user_id = (?) AND movie_id = (?)''',
                                           [userId, movieId]).fetchall()
        if (len(userRating) == 0):
            return []

        df = pd.read_sql_query("""Select movie_id , title from movies_metadata""", conn)
        df2 = pd.read_sql_query(
            """Select movie_id,rating from movie_rating where user_id=""" + str(userId) + """ AND movie_id =""" + str(
                movieId), conn)
        df3 = pd.read_sql_query("""Select user_id,movie_id,rating from movie_rating""", conn)
        df['movie_id'] = df['movie_id'].astype(str)
        df2['movie_id'] = df2['movie_id'].astype(str)
        df3['movie_id'] = df3['movie_id'].astype(str)
        # merged = pd.merge(df, df2)
        merged2 = pd.merge(df, df3)
        res = self.CollabBased(df2, merged2)
        return self.__extractRecommendationFromCollabDataframe(res, 0)

    def ContentWithUserId(self, userId, conn, numMovies):
        userRating = conn.cursor().execute('''SELECT * FROM movie_rating WHERE user_id = (?)''',
                                           [userId]).fetchall()
        if(len(userRating) == 0):
            return []
        df = pd.read_sql_query("""Select genres,movie_id from movies_metadata""", conn)
        df2 = pd.read_sql_query("""Select movie_id from movie_rating where user_id=""" + str(userId) + ''' AND rating > 2.5 ORDER BY RANDOM() LIMIT 5''', conn)
        merged = pd.merge(df, df2)
        pp = pd.Series()
        for movie_id in merged['movie_id'].values:
            pp = pp.append(self.Contentbased(movie_id, df, conn, numMovies))
        return self.__extractRecommendationFromContentDataFrame(pp)


    def CollabWithUserId(self, userId, conn):

        df = pd.read_sql_query("""Select movie_id , title from movies_metadata""", conn)
        df2 = pd.read_sql_query("""Select movie_id,rating from movie_rating where user_id=""" + str(userId), conn)
        df3 = pd.read_sql_query("""Select user_id,movie_id,rating from movie_rating""", conn)
        df['movie_id'] = df['movie_id'].astype(str)
        df2['movie_id'] = df2['movie_id'].astype(str)
        df3['movie_id'] = df3['movie_id'].astype(str)
        merged = pd.merge(df, df2)
        merged2 = pd.merge(df, df3)
        res = self.CollabBased(merged, merged2)
        return self.__extractRecommendationFromCollabDataframe(res, 4)

    def Contentbased(self, movieid, df, conn, numMovies):
        id = movieid
        x = df['movie_id'].dtype
        ind = df.loc[df['movie_id'] == int(id)]
        row_genre = df.at[ind.index.values[0], 'genres']
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
            temp = temp.append(self.__recommd(id, cosine_sim, indices, chunk, numMovies))
        return temp.to_frame()

    def __recommd(self, title, cosine_sim, indices, chunk, numMovies):

        # Get the index of the movie that matches the title
        idx = indices[title]

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True, )

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:numMovies + 1]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        v = chunk['movie_id'].iloc[movie_indices]
        # Return the top 10 most similar movies
        return v

    def CollabBased(self, merged, merged2):
        # make table where the index is userId and coloums is Book title and the values are rating
        user_rating = merged2.pivot_table(index='user_id', columns='movie_id', values='rating')

        # replace the Na values with 0
        user_rating = user_rating.fillna(0)

        # apply pearson rule for standaralization
        movie_similarity = user_rating.corr(method='pearson')

        similar_movie = pd.DataFrame()

        for index, row in merged.iterrows():
            similar_movie = similar_movie.append(
                self.__recommend_movie(row["movie_id"], row["rating"], movie_similarity), ignore_index=True)

        # similar_movie.sum().sort_values(ascending=False)
        retList = similar_movie.sum().sort_values(ascending=False).to_frame()
        return retList

        # function for getting recommendation

    def __recommend_movie(self, movie_id, user_rating, movie_similarity):
        if movie_id in movie_similarity:
            movie_score = movie_similarity[movie_id] * (user_rating - 2.5)
            movie_score = movie_score.sort_values(ascending=False)
            return movie_score

    def __extractRecommendationFromCollabDataframe(self, resDf, comNum):
        dfDict = resDf.to_dict()
        mList = []
        for movie in dfDict[0]:
            if dfDict[0][movie] > comNum:
                mList.append(movie)
        print(len(mList))
        shuffle(mList)
        try:
            return mList[:20]
        except:
            return mList

    def __extractRecommendationFromContentDataFrame(self, dfDict):
        mList = []
        for col in dfDict:
            for movie in dfDict[col]:
                if movie not in mList:
                    mList.append(movie)
        print(len(mList))
        shuffle(mList)
        try:
            return mList[:20]
        except:
            return mList
