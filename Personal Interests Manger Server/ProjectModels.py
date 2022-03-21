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

class SongModel:
    def __init__(self, youtubeId, image, artists, params = []):
        self.song_id = params[0]
        self.album_spotify_id = params[1]
        self.artists_spotify_id = params[2]
        self.duration = params[3]
        self.title = params[4]
        self.song_spotify_id = params[5]
        self.spotify_link = params[6]
        self.song_img = image
        self.ytId = youtubeId
        self.artists = artists

    def to_dict(song):
        if isinstance(song, SongModel):
            dict = {
                "song_id": song.song_id,
                "album_spotify_id": song.album_spotify_id,
                "artists_spotify_id": song.artists_spotify_id,
                "title": song.title,
                "song_spotify_id": song.song_spotify_id,
                "spotify_link": song.spotify_link,
                "youtube_id": song.ytId,
                "image": song.song_img,
                "artists": song.artists
            }
            return dict
        else:
            type_name = song.__class__.__name__
            raise TypeError("Unexpected type {0}".format(type_name))


class SongArtistModel:
    def __init__(self, params = []):
        self.artist_name = params[0]
        self.artist_spotify_id = params[1]
        self.image = params[2]
        self.followers = params[3]
        self.popularity = params[4]
        self.spotify_profile = params[5]

    def to_dict(artist):
        if isinstance(artist, SongArtistModel):
            dict = {
                "artist_name": artist.artist_name,
                "artist_spotify_id": artist.artist_spotify_id,
                "image": artist.image,
                "followers": artist.followers,
                "spotify_profile": artist.spotify_profile,
            }
            return dict
        else:
            type_name = artist.__class__.__name__
            raise TypeError("Unexpected type {0}".format(type_name))






class MediaItemPartialModel:
    def __init__(self, id, name, image, type):
        self.id = id
        self.name = name
        self.image = image
        self.type = type

    def to_dict(item):
        if isinstance(item, MediaItemPartialModel):
            return {
                "item_id": item.id,
                "item_name": item.name,
                "image": item.image,
                "type": item.type
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
