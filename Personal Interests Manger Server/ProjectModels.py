class MovieModel:
    def __init__(self, params=[]):
        self.adult = params[0]
        self.belong_to_collection = params[1]
        self.genres = params[2]
        self.movie_id = params[3]
        self.original_language = params[4]
        self.overview = params[5]
        self.popularity = params[6]
        self.poster = params[7]
        self.production_company = params[8]
        self.release_date = params[9]
        self.status = params[10]
        self.tag_line = params[11]
        self.title = params[12]
        self.vote_average = params[13]
        self.vote_count = params[14]
        self.imdb_id = params[15]
        self.year = params[16]
        self.trailer = params[17]
        self.background = params[18]

    def to_dict(movie):
        if isinstance(movie, MovieModel):
            dict = {
                "adult": movie.adult,
                "belong_to_collection": movie.belong_to_collection,
                "genres": movie.genres,
                "movie_id": movie.movie_id,
                "original_language": movie.original_language,
                "overview": movie.overview,
                "popularity": movie.popularity,
                "poster": movie.poster,
                "production_company": movie.production_company,
                "release_date": movie.release_date,
                "status": movie.status,
                "tag_line": movie.tag_line,
                "title": movie.title,
                "vote_average": movie.vote_average,
                "vote_count": movie.vote_count,
                "imdb_id": movie.imdb_id,
                "trailer": movie.trailer,
                "background": movie.background
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
            
class MediaItemPartialModel:
    def __init__(self, id, name, image):
        self.id = id
        self.name = name
        self.image = image

    def to_dict(item):
        if isinstance(item, MediaItemPartialModel):
            return {
                "item_id": item.id,
                "item_name": item.name,
                "image": item.image
            }
        else:
            type_name = item.__class__.__name__
            raise TypeError("Unexpected type {0}".format(type_name))


class SectionModel:
    def __init__(self, sectionName, itemList=[]):
        self.sectionName = sectionName
        self.itemList = itemList

    def to_dict(section):
        if isinstance(section, SectionModel):
            return {
                "section_name": section.sectionName,
                "items": section.itemList,
            }
        else:
            type_name = section.__class__.__name__
            raise TypeError("Unexpected type {0}".format(type_name))


