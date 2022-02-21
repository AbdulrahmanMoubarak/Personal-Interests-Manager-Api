import sqlite3
import pandas as pd
import json


def connectToDB():
    con = sqlite3.connect("pim_database.db")
    return con


def migrateMoviesMetadata():
    con = connectToDB()
    cur = con.cursor()

    ds = pd.read_csv("datasets/Movies/movies_metadata.csv")
    df = pd.DataFrame(ds)
    ids = []

    for row in df.iloc:
        if not row[4] in ids:
            ids.append(row[4])
            new_row = [row[0], row[1], row[2], row[3], row[4], row[6],
                       row[7], row[8],
                       row[9],
                       row[10],
                       row[11],
                       row[12],
                       row[13],
                       row[14],
                       row[15],
                       row[16],
                       row[17]]

            try:
                cur.execute("INSERT INTO movies_metadata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                            new_row)
                print(new_row)
            except:
                continue

    con.commit()
    con.close()


def migrateMovieRatings():
    con = connectToDB()
    cur = con.cursor()

    ds = pd.read_csv("datasets/Movies/ratings.csv")
    df = pd.DataFrame(ds)

    for row in df.iloc:
        new_row = [row[0], row[1], row[2], row[3]]
        try:
            cur.execute("INSERT INTO movie_rating VALUES (?, ?, ?, ?);", new_row)
            print(new_row)
        except:
            continue
    con.commit()
    con.close()


def migrateBookMetadata():
    con = connectToDB()
    cur = con.cursor()

    ds = pd.read_csv("datasets/Books/Books.csv")
    df = pd.DataFrame(ds)

    for row in df.iloc:
        new_row = [row[0], row[1], row[2], row[3], row[4], row[5]]

        try:
            cur.execute(
                "INSERT INTO books_metadata VALUES (?, ?, ?, ?, ?, ?);",
                new_row)
            print(new_row)
        except:
            continue

    con.commit()
    con.close()


def migrateBookRatings():
    con = connectToDB()
    cur = con.cursor()

    ds = pd.read_csv("datasets/Books/Ratings.csv")
    df = pd.DataFrame(ds)

    for row in df.iloc:
        new_row = [int(row[0]), row[1], int(row[2])]
        try:
            cur.execute("INSERT INTO book_rating VALUES (?, ?, ?);", new_row)
            print(new_row)
        except:
            continue

    con.commit()
    con.close()


def createMovieGenres():
    # [{'id': 12, 'name': 'Adventure'}, {'id': 28, 'name': 'Action'}, {'id': 878, 'name': 'Science Fiction'}]
    con = connectToDB()
    cur = con.cursor()
    cur.execute(''' SELECT movie_id, genres FROM movies_metadata WHERE genres LIKE "%id%" ''')
    movieGenreslist = cur.fetchall()
    con.close()
    new_movie_genres = dict()
    for rec in movieGenreslist:
        rec_str = str(rec[1]).replace("'", ''' " ''')
        genres = json.loads(rec_str)
        new_genres_str = ""

        for genre_obj in genres:
            genre_obj = dict(genre_obj)
            new_genres_str += list(genre_obj.values())[1] + "|"
        new_genres_str = new_genres_str[:-1]
        new_movie_genres[rec[0]] = new_genres_str

    return new_movie_genres


def updateMoviesGenresInDB():
    con = connectToDB()
    cur = con.cursor()
    movies_genres = createMovieGenres()

    for genre in movies_genres.items():
        rec = [genre[1], genre[0]]
        cur.execute("UPDATE movies_metadata SET genres = (?) WHERE movie_id = (?)", rec)
        print(rec)
    con.commit()
    con.close()

def createMetadataTableDB():
    con = connectToDB()
    cur = con.cursor()
    cur.execute(''' SELECT genres FROM movies_metadata  ''')
    composite_genres = cur.fetchall()

    unique_genres = dict()
    i = 0
    for genres_rec in composite_genres:
        genreList = str(genres_rec[0]).split('|')
        for genre in genreList:
            if genre not in unique_genres.values() and genre != '' and genre != 'None':
                unique_genres[i] = genre
                i += 1


    for genre in unique_genres.items():
        rec = [genre[0], genre[1]]
        cur.execute("INSERT INTO movie_genres VALUES (?, ?);", rec)
        print(rec)

    con.commit()
    con.close()