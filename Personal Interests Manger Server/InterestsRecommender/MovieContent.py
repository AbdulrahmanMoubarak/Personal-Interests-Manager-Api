import pandas as pd
import scipy
import threadpoolctl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

col_list = ["genres", "title"]
df = pd.read_csv("Movies.csv", usecols=col_list)

name = "Toy Story That Time Forgot"
ind = df[df['title'] == name].index.values[0]
row_genre = df.at[ind, 'genres']

result = None
hf=pd.DataFrame()

for chunk in pd.read_csv("Movies.csv", usecols=col_list, chunksize=7000):
    #chunk_result = voters_street.value_counts()
    chunk = chunk.reset_index()
    if not name in chunk.values:
        df2 = {'genres': row_genre, 'title': name}
        chunk = chunk.append(df2,ignore_index=True)


    chunk['genres'] = chunk['genres'].astype(str)
    tfidf = TfidfVectorizer(stop_words='english')

    #Replace NaN with an empty string
    chunk['genres'] = chunk['genres'].fillna('')

    #Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(chunk['genres'])

    #Output the shape of tfidf_matrix
    #tfidf_matrix.shape



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
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True,)

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:5]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return the top 10 most similar movies
        return chunk['title'].iloc[movie_indices]
    x = pd.DataFrame(get_recommendations('Toy Story That Time Forgot'))
    frames = [hf, x]
    hf = pd.concat(frames)

print(hf)