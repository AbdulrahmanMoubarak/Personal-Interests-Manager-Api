from flask import Flask, request
from MoviesManager import MoviesManager as movieManager
from BooksManager import BooksManager as bookManager
from MusicManager import MusicManager as musicManager

app = Flask(__name__)


@app.route("/movies/search", methods=['GET'])
def searchForMovie():
    search_query_genre = request.args.get('genre')
    search_query_name = request.args.get('name')
    search_query_id = request.args.get('id')
    if search_query_genre != None:
        return movieManager().findMovieByGenre(search_query_genre)
    elif search_query_name != None:
        return movieManager().findMovieByName(search_query_name)
    elif search_query_id != None:
        response = movieManager().findMovieById(search_query_id)
        return response

@app.route("/movies/rate", methods=['POST', 'GET'])
def rateMovie():
    if (request.method == 'GET'):
        param_userId = request.args.get('userId')
        param_movieId = request.args.get('movieId')
        param_rating = request.args.get('rating')
        if param_movieId != None and param_rating != None and param_userId != None:
            movieManager().addMovieRatingToDb(int(param_movieId), int(param_userId), float(param_rating))
        return
    elif (request.method == 'POST'):
        param_userId = request.form.get('userId')
        param_movieId = int(request.form.get('movieId'))
        param_rating = request.form.get('rating')
        if param_movieId != None and param_rating != None and param_userId != None:
            movieManager().addMovieRatingToDb(int(param_movieId), int(param_userId), float(param_rating))
        return

@app.route("/movies/main", methods=['GET'])
def getMoviesMainScreen():
    param_userId = request.args.get('userId')

    if param_userId != None:
        uId = param_userId
    response = movieManager().getHomePageMovies(param_userId)
    return response

@app.route("/movies/credits", methods=['GET'])
def getMovieCredits():
    param_movieId = request.args.get('movieId')
    if param_movieId != None:
        response = movieManager().findMovieCast(param_movieId)
        return response



@app.route("/books/search", methods=['GET'])  #Done
def searchForBook():
        search_query_id = request.args.get('id')
        search_query_name = request.args.get('name')
        search_query_author = request.args.get('author')
        if search_query_author != None:
            return bookManager().findBookByAuthor(search_query_author)
        elif search_query_name != None:
            return bookManager().findBookByName(search_query_name)
        elif search_query_id != None:
            response = bookManager().findBookById(search_query_id)
            return response

@app.route("/books/rate", methods=['POST', 'GET']) #Done
def rateBook():
    if (request.method == 'GET'):
        param_userId = request.args.get('user_id')
        param_bookId = request.args.get('isbn')
        param_rating = request.args.get('rating')
        if param_bookId != None and param_rating != None and param_userId != None:
            bookManager().addBookRatingToDb(int(param_userId), str(param_bookId), float(param_rating))
        return
    elif (request.method == 'POST'):
        param_userId = request.args.get('user_id')
        param_bookId = request.args.get('isbn')
        param_rating = request.args.get('rating')
        if param_bookId != None and param_rating != None and param_userId != None:
            bookManager().addBookRatingToDb(int(param_userId), str(param_bookId), float(param_rating))
        return

@app.route("/books/main", methods=['GET'])
def recommendBooks():
    param_userId = request.args.get('user_id')
    return None


@app.route("/music/search", methods=['GET'])
def searchForSong():
    search_query = request.args.get('query')
    search_query_id = request.args.get('id')
    if search_query_id != None:
        return musicManager().findSongById(search_query_id)
    return

@app.route("/music/main", methods=['GET'])
def getSongsMainScreen():
    param_userId = request.args.get('userId')

    if param_userId != None:
        uId = param_userId
    response = musicManager().getHomePageSongs(param_userId)
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)
