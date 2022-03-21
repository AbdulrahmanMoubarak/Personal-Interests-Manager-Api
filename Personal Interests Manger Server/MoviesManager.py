import sqlite3
import json
from random import randrange

from tmdbv3api import TMDb
from TMDBCredentials import TmdbCredentials
from ProjectModels import MovieModel
from ProjectModels import MediaItemPartialModel
from ProjectModels import SectionModel
from datetime import datetime, date
from tmdbv3api import Trending
from tmdbv3api import Movie
from tmdbv3api import Discover
from random import shuffle

tmdb = TMDb()
tmdb.language = 'en'
tmdb.debug = True
tmdb.api_key = TmdbCredentials.API_KEY

class MoviesManager:
    def __connectToDB(self):
        con = sqlite3.connect(
            "D:/FCIS SWE 2021/Graduation Project/Project source code/Dataset Migration/pim_database.db")
        return con

    def getHomePageMovies(self, userId):
        randomYear = randrange(1975, int(date.today().year))
        randomGenre = self.__getRandomGenre()

        tmdbTrendingDay = self.__getDayTrendingMovies()
        tmdbTrendingWeek = self.__getWeekTrendingMovies()
        tmdbDiscoverYear = self.__getMoviesFromTmdbDiscover(randomYear)
        tmdbDiscoverGenre = self.__getRandomGenreMoviesFromTmdb(randomGenre[0])
        tmdbUpcoming = self.__getUpcomingMovies()
        tmdbTopRated = self.__getRandomTopRatedMovies()

        trendinDay = SectionModel("Trending Today", tmdbTrendingDay)
        trendinWeek = SectionModel("Trending This Week", tmdbTrendingWeek)
        yearMovies = SectionModel("Popular in " + str(randomYear), tmdbDiscoverYear)
        genreMovies = SectionModel("Popular " + randomGenre[1] + " Movies", tmdbDiscoverGenre)
        upcomingMovies = SectionModel("Upcoming Movies", tmdbUpcoming)
        topMovies = SectionModel("Of Top Rated Movies", tmdbTopRated)
        secList = [trendinDay, trendinWeek, topMovies, yearMovies, genreMovies, upcomingMovies]
        shuffle(secList)
        return json.dumps(secList, default=SectionModel.to_dict)

    def findMovieCast(self, movieId):
        tmdb_movie = Movie()
        response = tmdb_movie.credits(movieId)
        cast = self.__extractCastFromResponse(response)
        return json.dumps(cast, default=MediaItemPartialModel.to_dict)

    def __extractCastFromResponse(self, response):
        cList = []
        for castMember in response['cast']:
            cImage = castMember['profile_path']
            cName = castMember['name']
            cChar = castMember['character']
            cList.append(MediaItemPartialModel(cChar, cName, cImage, type="cast_member"))
            i+=1
        return cList


    def findMovieByGenre(self, genre):
        mList = []
        movieList = self.__findSimilarMoviesInDbByGenre("%" + genre + "%")
        for movie in movieList:
            mId = movie[0]
            mTitle = movie[1]
            mPoster = movie[2]
            mList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(mId, mTitle, mPoster, "movie")))

        tmdb_movieList = self.__tmdbSearchForMovie(genre)
        mySearchSec = SectionModel("Search Results", mList)
        tmdbSearchSec = SectionModel("Results From TMDB", tmdb_movieList)

        secList = [mySearchSec, tmdbSearchSec]

        return json.dumps(secList, default=SectionModel.to_dict)

    def findMovieByName(self, name):
        mList = []
        movieList = self.__findSimilarMoviesInDbByName("%" + name + "%")
        for movie in movieList:
            mId = movie[0]
            mTitle = movie[1]
            mPoster = movie[2]
            mList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(mId, mTitle, mPoster, "movie")))

        tmdb_movieList = self.__tmdbSearchForMovie(name)

        mySearchSec = SectionModel("Search Results", mList)
        tmdbSearchSec = SectionModel("Results From TMDB", tmdb_movieList)

        secList = [mySearchSec, tmdbSearchSec]

        return json.dumps(secList, default=SectionModel.to_dict)

    def findMovieById(self, id):
        id = int(id)
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute('''SELECT * FROM movies_metadata WHERE movie_id = (?)''', [id])
        result = cur.fetchall()
        con.close()
        if len(result) == 0:
            return json.dumps(self.__tmdbGetMovieById(id), default=MovieModel.to_dict)
        else:
            return json.dumps(MovieModel(result[0]), default=MovieModel.to_dict)

    def __findSimilarMoviesInDbByName(self, movie):
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute(
            ''' SELECT movie_id, title, poster FROM movies_metadata WHERE title like (?) ORDER BY popularity DESC LIMIT 20 OFFSET 0''',
            [movie])
        result = cur.fetchall()
        con.close()
        return result

    def __findSimilarMoviesInDbByGenre(self, genres):
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute(
            ''' SELECT movie_id, title, poster FROM movies_metadata WHERE genres like (?) ORDER BY popularity DESC LIMIT 20 OFFSET 0''',
            [genres])
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

    def __tmdbSearchForMovie(self, query=""):
        tmdb_movies = Movie()
        results = tmdb_movies.search(query)
        mList = []
        for movie in results:
            mId = movie['id']
            mTitle = movie['title']
            mPoster = movie['poster_path']
            mList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(mId, mTitle, mPoster, "movie")))
        return mList

    def __tmdbGetMovieById(self, mId):
        try:
            mDetails = Movie().details(mId)
        except:
            return
        return MovieModel(self.__processTMDBMovieDetails(mDetails))

    def recommendMoviesByUserId(self):
        return

    def __getDayTrendingMovies(self):
        trending = Trending()
        tmdb_trendingDay = trending.all_day(1)
        mList = []
        for movie in tmdb_trendingDay:
            try:
                mId = movie['id']
                mTitle = movie['title']
                mPoster = movie['poster_path']
            except:
                continue
            mList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(mId, mTitle, mPoster, "movie")))
        return mList

    def __getUpcomingMovies(self):
        tmdb_movies = Movie()
        results = tmdb_movies.upcoming()
        mList = []
        for movie in results:
            mId = movie['id']
            mTitle = movie['title']
            mPoster = movie['poster_path']
            mList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(mId, mTitle, mPoster, "movie")))
        return mList

    def __getRandomTopRatedMovies(self):
        tmdb_movies = Movie()
        results = tmdb_movies.top_rated(randrange(1, 10))
        mList = []
        for movie in results:
            mId = movie['id']
            mTitle = movie['title']
            mPoster = movie['poster_path']
            mList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(mId, mTitle, mPoster, "movie")))
        return mList

    def __getWeekTrendingMovies(self):
        trending = Trending()
        tmdb_trendingDay = trending.all_week(1)
        mList = []
        for movie in tmdb_trendingDay:
            try:
                mId = movie['id']
                mTitle = movie['title']
                mPoster = movie['poster_path']
            except:
                continue
            mList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(mId, mTitle, mPoster, "movie")))
        return mList

    def __getMoviesFromTmdbDiscover(self, year):
        tmdb_discover = Discover()
        res = tmdb_discover.discover_movies(
            {"primary_release_year": str(year), "sort_by": "popularity.desc", "language": "en-US",
             "page": randrange(1, 10)})
        mList = []
        for movie in res:
            try:
                mId = movie['id']
                mTitle = movie['title']
                mPoster = movie['poster_path']
            except:
                continue
            mList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(mId, mTitle, mPoster, "movie")))
        return mList

    def __getRandomGenre(self):
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute(''' SELECT genre_id, genre_name FROM movie_genres''')
        genres = cur.fetchall()
        randIndex = randrange(0, len(genres) - 1)
        con.close()
        return genres[randIndex]

    def __getRandomGenreMoviesFromTmdb(self, genre):
        tmdb_discover = Discover()
        res = tmdb_discover.discover_movies(
            {"with_genres": str(genre), "sort_by": "popularity.desc", "language": "en-US", "page": randrange(1, 10)})
        mList = []
        for movie in res:
            try:
                mId = movie['id']
                mTitle = movie['title']
                mPoster = movie['poster_path']
            except:
                continue
            mList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(mId, mTitle, mPoster, "movie")))
        return mList


    def __processTMDBMovieDetails(self, mDetails):
        mId = mDetails['id']
        mAdult = mDetails['adult']
        mTitle = mDetails['title']
        mOverview = mDetails['overview']
        mBackground = mDetails['backdrop_path']
        mCollection = mDetails['belongs_to_collection']
        if mCollection != None:
            mCollection = mCollection['name']
        mGenres = ""
        for gen in mDetails['genres']:
            mGenres += gen['name'] + "|"
        mLanguage = mDetails['original_language']
        mPopularity = float(mDetails['popularity'])
        mPoster = mDetails['poster_path']
        try:
            mYear = int(str(mDetails['release_date']).split('-')[0])
        except:
            mYear = 0
        try:
            mDate = mDetails['release_date']
        except:
            mDate = "Unknown"
        mStatus = mDetails['status']
        mTrailer = ""
        try:
            for trailer in mDetails['trailers']['youtube']:
                if trailer['type'] == 'Trailer':
                    mTrailer = trailer['source']
                    if trailer['name'] == 'Official IMAX® Trailer':
                        break
        except:
            mTrailer = "None"
        mVoteAverage = float(mDetails['vote_average'])
        mVoteCount = int(mDetails['vote_count'])
        mTagline = mDetails['tagline']
        mImdbId = mDetails['imdb_id']
        mProductionCompanies = ""
        for comp in mDetails['production_companies']:
            mProductionCompanies += comp['name'] + "|"
        return [mAdult, mCollection, mGenres, mId, mLanguage, mOverview, mPopularity, mPoster, mProductionCompanies,
                mDate,
                mStatus, mTagline, mTitle, mVoteAverage, mVoteCount, mImdbId,
                mYear,
                mTrailer,
                mBackground
                ]


