from flask import Flask, request, jsonify
from MoviesManager import MoviesManager as movieManager
from BooksManager import BooksManager as bookManager
from MusicManager import MusicManager as musicManager
import asyncio
import threading

app = Flask(__name__)


@app.route("/movies/search", methods=['GET'])
def searchForMovie():
    search_query_genre = request.args.get('genre')
    search_query_name = request.args.get('name')
    search_query_id = request.args.get('id')
    param_userId = request.args.get('userId')
    if search_query_genre != None:
        return movieManager().findMovieByGenre(search_query_genre)
    elif search_query_name != None:
        return movieManager().findMovieByName(search_query_name)
    elif search_query_id != None and param_userId != None:
        response = movieManager().findMovieById(search_query_id, param_userId)
        return response

#526896
@app.route("/movies/rate", methods=['POST'])
def rateMovie():
    if (request.method == 'POST'):
        param_userId = request.form.get('userId')
        param_movieId = request.form.get('movieId')
        param_rating = request.form.get('rating')
        if param_movieId != None and param_rating != None and param_userId != None:
            ret = movieManager().addMovieRatingToDb(int(param_movieId), int(param_userId), float(param_rating))
            if ret:
                return jsonify({"message": "Ok"}), 200
            else:
                return jsonify({"message": "Bad Request"}), 409


@app.route("/movies/main", methods=['GET'])
def getMoviesMainScreen():

    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()

    param_userId = request.args.get('userId')

    if param_userId != None:
        uId = param_userId
    response = loop.run_until_complete(movieManager().getHomePageMovies(param_userId))
    return response


@app.route("/movies/credits", methods=['GET'])
def getMovieCredits():
    param_movieId = request.args.get('movieId')
    if param_movieId != None:
        response = movieManager().findMovieCast(param_movieId)
        return response


@app.route("/movies/movie-based-recommendation", methods=['GET'])
def getMovieBasedRecommendation():
    param_movieId = request.args.get('movieId')
    param_userId = request.args.get('userId')
    if param_movieId != None:
        response = movieManager().getMovieBasedRecommendation(param_movieId, param_userId)
        return response


@app.route("/books/search", methods=['GET'])  # Done
def searchForBook():
    search_query_id = request.args.get('id')
    search_query = request.args.get('q')
    param_user_id = request.args.get('userId')
    search_query_name = request.args.get('name')
    search_query_author = request.args.get('author')
    if search_query_author != None:
        return bookManager().findBookByAuthor(search_query_author)
    elif search_query_name != None:
        return bookManager().findBookByName(search_query_name)
    elif search_query_id != None and param_user_id != None:
        return bookManager().findBookById(search_query_id, param_user_id)
    elif search_query != None:
        return bookManager().searchForBook(search_query)


@app.route("/books/rate", methods=['POST'])  # Done
def rateBook():
    if (request.method == 'POST'):
        param_userId = request.form.get('userId')
        param_bookId = request.form.get('bookId')
        param_bookName = request.form.get('bookName')
        param_rating = request.form.get('rating')
        if param_bookId != None and param_rating != None and param_userId != None and param_bookName != None:
            ret = bookManager().addBookRatingToDb(int(param_userId), str(param_bookId), float(param_rating), str(param_bookName))
            if ret:
                return jsonify({"message": "Ok"}), 200
            else:
                return jsonify({"message": "Bad Request"}), 409


@app.route("/books/main", methods=['GET'])
def recommendBooks():

    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()

    param_userId = request.args.get('userId')
    if param_userId != None:
        response = loop.run_until_complete(bookManager().getHomePageBooks(param_userId))
        return response

@app.route("/books/book-based-recommendation", methods=['GET'])
def getBookBasedRecommendation():
    param_bookId = request.args.get('bookId')
    if param_bookId != None:
        response = bookManager().getBookBasedRecommendation(param_bookId)
        return response


@app.route("/music/search", methods=['GET'])
def searchForSong():
    search_query = request.args.get('query')
    search_query_id = request.args.get('id')
    if search_query_id != None:
        return musicManager().findSongById(search_query_id)
    elif search_query != None:
        return musicManager().searchForSong(search_query)
    return


@app.route("/music/main", methods=['GET'])
def getSongsMainScreen():

    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()

    param_userId = request.args.get('userId')

    if param_userId != None:
        response = loop.run_until_complete(musicManager().getHomePageSongs(param_userId))
        return response


@app.route("/music/song-based-recommendation", methods=['GET'])
def getSongBasedRecommendation():
    param_songId = request.args.get('songId')
    return musicManager().getSongBasedRecommendation(param_songId)


@app.route("/song/listening", methods=['POST'])
def incrementplayingtime():
    param_userId = request.form.get('userId')
    param_songId = request.form.get('songId')
    if param_userId != None and param_songId != None:
        ret = musicManager().addSonglistening(int(param_userId), str(param_songId))
        if ret:
            return jsonify({"message": "Ok"}), 200
        else:
            return jsonify({"message": "Bad Request"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5001)
