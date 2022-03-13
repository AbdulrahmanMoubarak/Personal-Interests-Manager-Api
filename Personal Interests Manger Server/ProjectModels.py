class MovieModel:
    def __init__(self, params=[]):
        self.adult = params[0]
        self.belong_to_collection = params[1]
        self.budget = params[2]
        self.genres = params[3]
        self.movie_id = params[4]
        self.original_language = params[5]
        self.overview = params[6]
        self.popularity = params[7]
        self.poster = params[8]
        self.production_company = params[9]
        self.release_date = params[10]
        self.runtime = params[11]
        self.status = params[12]
        self.tag_line = params[13]
        self.title = params[14]
        self.vote_average = params[15]
        self.vote_count = params[16]

    def to_dict(movie):
        if isinstance(movie, MovieModel):
            dict = {
                "adult": movie.adult,
                "belong_to_collection": movie.belong_to_collection,
                "budget": movie.budget,
                "genres": movie.genres,
                "movie_id": movie.movie_id,
                "original_language": movie.original_language,
                "overview": movie.overview,
                "popularity": movie.popularity,
                "poster": movie.poster,
                "production_company": movie.production_company,
                "release_date": movie.release_date,
                "runtime": movie.runtime,
                "status": movie.status,
                "tag_line": movie.tag_line,
                "title": movie.title,
                "vote_average": movie.vote_average,
                "vote_count": movie.vote_count,
            }
            return dict
        else:
            type_name = movie.__class__.__name__
            raise TypeError("Unexpected type {0}".format(type_name))
          
        
  class BooksModel:
    def __init__(self, params=[]):
        self.isbn = params[0]
        self.book_title = params[1]
        self.book_author = params[2]
        self.year_of_publication = params[3]
        self.publisher = params[4]
        self.image_url = params[5]


    def to_dict(book):
        if isinstance(book, BooksModel):
            dict = {
                "isbn": book.isbn,
                "book_title": book.book_title,
                "book_author": book.book_author,
                "year_of_publication": book.year_of_publication,
                "publisher": book.publisher,
                "image_url": book.image_url,

            }
            return dict
        else:
            type_name = book.__class__.__name__
            raise TypeError("Unexpected type {0}".format(type_name))

