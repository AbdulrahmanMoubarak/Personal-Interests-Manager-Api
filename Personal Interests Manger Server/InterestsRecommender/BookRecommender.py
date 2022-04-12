import pandas as pd
import scipy
import threadpoolctl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import sqlite3

conn = sqlite3.connect("pim_database.db")


class Book:
    def ContentWithUserId(self,userId):
        df = pd.read_sql_query("""Select book_title,isbn from books_metadata""", conn)
        df2 = pd.read_sql_query("""Select isbn from book_rating where user_id=""" + str(userId), conn)
        merged = pd.merge(df, df2)
        start = 0;
        pp = pd.Series()
        for Book_id in merged['isbn'].values:
            if start == 0:
                pp=pp.append(self.Contentbased(Book_id, df, start))
            else:
                start = start + 6
                pp=pp.append(self.Contentbased(Book_id, df, start))
        return pp

    def Contentbased(self,Book_id, df, start):
        id = Book_id
        ind = df[df['isbn'] == id].index.values[0]
        row_genre = df.at[ind, 'book_title']

        temp = pd.Series()
        result = None
        ch = 0
        end = 0
        for chunk in pd.read_sql_query("""Select book_title,isbn from books_metadata""", conn, chunksize=6000):
            # chunk_result = voters_street.value_counts()

            if ch < start:
                ch = ch + 1
                continue
            if end > 5:
                break

            chunk = chunk.reset_index()
            if not id in chunk["isbn"].unique():
                df2 = {'book_title': row_genre, 'isbn': id}
                chunk = chunk.append(df2, ignore_index=True)

            chunk['book_title'] = chunk['book_title'].astype(str)
            tfidf = TfidfVectorizer(stop_words='english')

            # Replace NaN with an empty string
            chunk['book_title'] = chunk['book_title'].fillna('')

            # Construct the required TF-IDF matrix by fitting and transforming the data
            tfidf_matrix = tfidf.fit_transform(chunk['book_title'])

            # Output the shape of tfidf_matrix
            # tfidf_matrix.shape

            # Compute the cosine similarity matrix
            cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
            # Construct a reverse map of indices and movie titles
            indices = pd.Series(chunk.index, index=chunk['isbn']).drop_duplicates()

            # Function that takes in movie title as input and outputs most similar movies

            temp = temp.append(self.__recommendations(id,cosine_sim,indices,chunk))
            end = end + 1

        return (temp)

    def __recommendations(self,id,cosine_sim,indices,chunk):
        # Get the index of the movie that matches the title
        idx = indices[id]

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True, )

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:2]

        # Get the movie indices
        Book_indices = [i[0] for i in sim_scores]

        # Return the top 10 most similar movies
        return chunk['book_title'].iloc[Book_indices]


r=Book()
print (r.ContentWithUserId(276729))
