import asyncio
import gc
from flask import Flask, request, jsonify

from app.BooksManager import BooksManager as bookManager
from app.MoviesManager import MoviesManager as movieManager
from app.MusicManager import MusicManager as musicManager
from app.UserManager import UserManager as userManager

app = Flask(__name__)


@app.route("/", methods=['GET'])
def index():
    return jsonify({"message": "Ok"}), 200


@app.route("/register", methods=['POST'])
def registerUser():
    param_username = request.form.get("userName")
    param_email = request.form.get("email")
    param_password = request.form.get("password")
    res = userManager().registerUser(param_email, param_password, param_username)
    if (res):
        resp = jsonify({"message": "Ok"}), 200
    else:
        resp = jsonify({"message": "Email already exists"}), 409
    gc.collect()
    return resp


@app.route("/register/preferences", methods=['POST'])
def registerUserPreferences():
    param_artists = request.form.get("favArtists")
    param_genres = request.form.get("favGenres")
    param_email = request.form.get("email")
    res = userManager().addUserPreferences(param_artists, param_genres, param_email)
    if (res):
        resp = jsonify({"message": "Ok"}), 200
    else:
        resp = jsonify({"message": "Email already exists"}), 409
    gc.collect()
    return resp


@app.route("/login", methods=['POST'])
def userLogin():
    param_email = request.form.get("email")
    param_pass = request.form.get("password")
    resp = userManager().login(param_email, param_pass)
    gc.collect()
    return resp


@app.route("/playlist/create", methods=['POST'])
def createPlaylist():
    param_userId = request.form.get("userId")
    param_name = request.form.get("name")
    param_type = request.form.get("type")
    res = userManager().createPlaylist(param_userId, param_name, param_type)
    if (res):
        resp = jsonify({"message": "Ok"}), 200
    else:
        resp = jsonify({"message": "Email already exists"}), 409
    gc.collect()
    return resp

@app.route("/playlist/add-item", methods=['POST'])
def addPlaylistItem():
    param_playlistId = request.form.get("playlistId")
    param_itemId = request.form.get("itemId")
    param_itemName = request.form.get("itemName")
    param_itemImage = request.form.get("itemImage")
    res = userManager().addPlaylistItem(param_playlistId, param_itemId, param_itemName, param_itemImage)
    if (res):
        resp = jsonify({"message": "Ok"}), 200
    else:
        resp = jsonify({"message": "Email already exists"}), 409
    gc.collect()
    return resp

@app.route("/playlist/get", methods=['GET'])
def getAllUserPlaylists():
    param_userId = request.args.get("userId")
    param_type = request.args.get("type")
    if param_type != None:
        resp = userManager().getAllPlaylistsOfType(param_userId, param_type)
    else:
        resp = userManager().getAllPlaylists(param_userId)
    gc.collect()
    return resp

@app.route("/playlist/items", methods=['GET'])
def getAllPlaylistItems():
    param_plId = request.args.get("playlistId")
    resp = userManager().getUserPlaylistItems(param_plId)
    gc.collect()
    return resp

@app.route("/movies/search", methods=['GET'])
def searchForMovie():
    search_query_genre = request.args.get('genre')
    search_query_name = request.args.get('name')
    search_query_id = request.args.get('id')
    param_userId = request.args.get('userId')
    param_lang = request.args.get('lang')

    if search_query_genre != None:
        resp = movieManager().findMovieByGenre(search_query_genre)
    elif search_query_name != None:
        resp = movieManager().findMovieByName(search_query_name, param_lang)
    elif search_query_id != None and param_userId != None:
        resp = movieManager().findMovieById(search_query_id, param_userId, param_lang)
    else:
        resp = jsonify({"message": "Bad Request"}), 409
    gc.collect()
    return resp


# 526896
@app.route("/movies/rate", methods=['POST'])
def rateMovie():
    if (request.method == 'POST'):
        param_userId = request.form.get('userId')
        param_movieId = request.form.get('movieId')
        param_rating = request.form.get('rating')
        if param_movieId != None and param_rating != None and param_userId != None:
            ret = movieManager().addMovieRatingToDb(int(param_movieId), int(param_userId), float(param_rating))
            if ret:
                resp = jsonify({"message": "Ok"}), 200
            else:
                resp = jsonify({"message": "Bad Request"}), 409
        else:
            resp = jsonify({"message": "Bad Request"}), 409
        gc.collect()
        return resp


@app.route("/movies/main/sections", methods=['GET'])
def getMoviesMainSections():
    param_userId = request.args.get("userId")
    param_lang = request.args.get("lang")
    response = movieManager().getHomePageSectionNames(param_userId, param_lang)
    gc.collect()
    return response


@app.route("/movies/main/sections/content", methods=['GET'])
def getSectionContents():
    name = request.args.get('name').replace('+', ' ')
    userId = request.args.get('userId')
    year = request.args.get('year')
    genre = request.args.get('genre')
    lang = request.args.get('lang')
    if name != None:
        resp = movieManager().getSectionContent(name, userId, year, genre, lang)
        gc.collect()
        return resp


@app.route("/movies/main", methods=['GET'])
def getMoviesMainScreen():
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()

    param_userId = request.args.get('userId')

    if param_userId != None:
        uId = param_userId
    response = loop.run_until_complete(movieManager().getHomePageMovies(param_userId))
    gc.collect()
    return response


@app.route("/movies/credits", methods=['GET'])
def getMovieCredits():
    param_movieId = request.args.get('movieId')
    param_language = request.args.get('lang')
    if param_movieId != None:
        response = movieManager().findMovieCast(param_movieId, param_language)
        gc.collect()
        return response


@app.route("/movies/movie-based-recommendation", methods=['GET'])
def getMovieBasedRecommendation():
    param_movieId = request.args.get('movieId')
    param_userId = request.args.get('userId')
    param_lang = request.args.get('lang')
    if param_movieId != None:
        response = movieManager().getMovieBasedRecommendation(param_movieId, param_userId, param_lang)
        gc.collect()
        return response


@app.route("/books/search", methods=['GET'])  # Done
def searchForBook():
    search_query_id = request.args.get('id')
    search_query = request.args.get('q')
    search_lang = request.args.get('lang')
    param_user_id = request.args.get('userId')
    search_query_name = request.args.get('name')
    search_query_author = request.args.get('author')
    if search_query_author != None:
        resp = bookManager().findBookByAuthor(search_query_author)
    elif search_query_name != None:
        resp = bookManager().findBookByName(search_query_name)
    elif search_query_id != None and param_user_id != None:
        resp = bookManager().findBookById(search_query_id, param_user_id, search_lang)
    elif search_query != None:
        resp = bookManager().searchForBook(search_query, search_lang)
    else:
        resp = jsonify({"message": "Ok"}), 200
    gc.collect()
    return resp


@app.route("/books/rate", methods=['POST'])  # Done
def rateBook():
    if (request.method == 'POST'):
        param_userId = request.form.get('userId')
        param_bookId = request.form.get('bookId')
        param_bookName = request.form.get('bookName')
        param_rating = request.form.get('rating')
        if param_bookId != None and param_rating != None and param_userId != None and param_bookName != None:
            ret = bookManager().addBookRatingToDb(int(param_userId), str(param_bookId), float(param_rating),
                                                  str(param_bookName))
            gc.collect()
            if ret:
                return jsonify({"message": "Ok"}), 200
            else:
                return jsonify({"message": "Bad Request"}), 409


@app.route("/books/main", methods=['GET'])
def recommendBooks():
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()

    param_userId = request.args.get('userId')
    param_lang = request.args.get('lang')
    if param_userId != None:
        response = loop.run_until_complete(bookManager().getHomePageBooks(param_userId, param_lang))
        gc.collect()
        return response


@app.route("/books/book-based-recommendation", methods=['GET'])
def getBookBasedRecommendation():
    param_bookId = request.args.get('bookId')
    param_lang = request.args.get('lang')
    if param_bookId != None:
        response = bookManager().getBookBasedRecommendation(param_bookId, param_lang)
        gc.collect()
        return response


@app.route("/music/search", methods=['GET'])
def searchForSong():
    search_query = request.args.get('query')
    search_query_id = request.args.get('id')
    if search_query_id != None:
        gc.collect()
        return musicManager().findSongById(search_query_id)
    elif search_query != None:
        gc.collect()
        return musicManager().searchForSong(search_query)
    return


@app.route("/music/main", methods=['GET'])
def getSongsMainScreen():
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()

    param_userId = request.args.get('userId')
    param_lang = request.args.get('lang')

    if param_userId != None:
        response = loop.run_until_complete(musicManager().getHomePageSongs(param_userId, param_lang))
        gc.collect()
        return response


@app.route("/music/top-artists", methods=['GET'])
def getTopArtists():
    resp = musicManager().getTopSongArtists()
    gc.collect()
    return resp


@app.route("/music/genres", methods=['GET'])
def getSongGenres():
    resp = musicManager().getSongGenres()
    gc.collect()
    return resp


@app.route("/music/song-based-recommendation", methods=['GET'])
def getSongBasedRecommendation():
    param_songId = request.args.get('songId')
    param_lang = request.args.get('lang')
    resp = musicManager().getSongBasedRecommendation(param_songId, param_lang)
    gc.collect()
    return resp


@app.route("/song/listening", methods=['POST'])
def incrementplayingtime():
    param_userId = request.form.get('userId')
    param_songId = request.form.get('songId')
    if param_userId != None and param_songId != None:
        ret = musicManager().addSonglistening(int(param_userId), str(param_songId))
        gc.collect()
        if ret:
            return jsonify({"message": "Ok"}), 200
        else:
            return jsonify({"message": "Bad Request"}), 400

@app.route("/song/local-music-upload", methods=['POST'])
def updateUserLocalMusicData():
    param_userId = request.form.get('userId')
    param_songs = request.form.getlist('songs[]')
    if param_userId != None and param_songs != None:
        ret = musicManager().addUserLocalMusic(int(param_userId), param_songs)
        gc.collect()
        if ret:
            return jsonify({"message": "Ok"}), 200
        else:
            return jsonify({"message": "Bad Request"}), 400


def getApp():
    return app
