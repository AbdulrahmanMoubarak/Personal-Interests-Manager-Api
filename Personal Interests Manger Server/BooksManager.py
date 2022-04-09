import sqlite3
import json
from ProjectModels import MovieModel , BooksModel
from datetime import datetime


class BooksManager:

    def __connectToDB(self):
        con = sqlite3.connect("pim_database.db")
        return con

    def findBookByAuthor(self, author): #Done
        bList = []
        bookList = self.__findSimilarBooksInDbByAuthor("%" + author + "%")
        for book in bookList:
            bModel = BooksModel(book)
            bList.append(bModel)
        return json.dumps(bList, default=BooksModel.to_dict)

       # Search by title:
    def findBookByName(self, name): #Done
        bList = []
        bookList = self.__findSimilarBooksInDbByName("%" + name + "%")
        for book in bookList:
            bModel = BooksModel(book)
            bList.append(bModel)
        return json.dumps(bList, default=BooksModel.to_dict)

    def findBookById(self, id):  #Done
        id = str(id)
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute('''SELECT * FROM books_metadata WHERE isbn = (?)''', [id])
        result = cur.fetchall()[0]
        con.close()
        return json.dumps(BooksModel(result), default=BooksModel.to_dict)

    def __findSimilarBooksInDbByName(self, name): #Done
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute(''' SELECT * FROM books_metadata WHERE book_title like (?) ''', [name])
        result = cur.fetchall()
        con.close()
        return result

    def __findSimilarBooksInDbByAuthor(self, authors):  #Done
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute(''' SELECT * FROM books_metadata WHERE book_author like (?) ''', [authors])
        result = cur.fetchall()
        con.close()
        return result

    def addBookRatingToDb(self, user_id, isbn, rating): #Done
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute('''INSERT INTO book_rating VALUES (?,?,?)''', [user_id, isbn, rating])
        con.close()
        return


