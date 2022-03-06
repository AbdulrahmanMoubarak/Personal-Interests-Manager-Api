from flask import Flask, request
from MoviesManager import MoviesManager as movieManager

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
        param_movieId = request.form.get('movieId')
        param_rating = request.form.get('rating')
        if param_movieId != None and param_rating != None and param_userId != None:
            movieManager().addMovieRatingToDb(int(param_movieId), int(param_userId), float(param_rating))
        return

@app.route("/movies/recommend", methods=['GET'])
def recommendMovies():
    param_userId = request.args.get('userId')
    return None


@app.route("/book/search", methods=['GET'])
def searchForBook():
    return


if __name__ == "__main__":
    app.run(debug=True, port=5001)
# movies search --Done
# movie recommendation --Done
# book Search
# Book recommendation
# Scrapper search
# User post
# song search
# song recommendation
# chatbot (get-post)
# http://127.0.0.1:5000/
