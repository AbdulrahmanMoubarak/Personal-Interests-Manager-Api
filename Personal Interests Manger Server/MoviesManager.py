import sqlite3
import json
from ProjectModels import MovieModel
from datetime import datetime


class MoviesManager:

    def __connectToDB(self):
        con = sqlite3.connect("pim_database.db")
        return con

    def findMovieByGenre(self, genre):
        mList = []
        movieList = self.__findSimilarMoviesInDbByGenre("%" + genre + "%")
        for movie in movieList:
            mModel = MovieModel(movie)
            mList.append(mModel)
        return json.dumps(mList, default=MovieModel.to_dict)

    def findMovieByName(self, name):
        mList = []
        movieList = self.__findSimilarMoviesInDbByName("%" + name + "%")
        for movie in movieList:
            mModel = MovieModel(movie)
            mList.append(mModel)
        return json.dumps(mList, default=MovieModel.to_dict)

    def findMovieById(self, id):
        id = int(id)
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute('''SELECT * FROM movies_metadata WHERE movie_id = (?)''', [id])
        result = cur.fetchall()[0]
        con.close()
        return json.dumps(MovieModel(result), default=MovieModel.to_dict)

    def __findSimilarMoviesInDbByName(self, movie):
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute(''' SELECT * FROM movies_metadata WHERE title like (?) ''', [movie])
        result = cur.fetchall()
        con.close()
        return result

    def __findSimilarMoviesInDbByGenre(self, genres):
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute(''' SELECT * FROM movies_metadata WHERE genres like (?) ''', [genres])
        result = cur.fetchall()
        con.close()
        return result

    def addMovieRatingToDb(self, movieId, userId, rating):
        con = self.__connectToDB()
        cur = con.cursor()
        timestamp = datetime.now().timestamp()
        cur.execute('''INSERT INTO movie_rating VALUES (?,?,?,?)''', [userId, movieId, rating, timestamp])
        con.close()
        return


