import sqlite3
import json
from ProjectModels import BooksModel
from ProjectModels import SectionModel
import urllib.parse
from urllib.request import urlopen
from ProjectModels import MediaItemPartialModel
from random import shuffle
from concurrent.futures.thread import ThreadPoolExecutor
from random import shuffle
from random import randrange
import aiohttp
import asyncio


class BooksManager:
    def __connectToDB(self):
        con = sqlite3.connect("D:/FCIS SWE 2021/Graduation Project/Project source code/Dataset Migration/pim_database.db")
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

    def findBookById(self, id, userId):  #Done
        urlQueryText = id
        api = "https://www.googleapis.com/books/v1/volumes?q=" + urlQueryText +"&maxResults=1"
        resp  = urlopen(api)
        book_data = json.load(resp)
        return json.dumps(BooksModel(self.__extractBookDetails(book_data, userId)), default=BooksModel.to_dict)

    def __extractBookDetails(self, bookData, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        try:
            isbn = bookData['items'][0]['industryIdentifiers'][1]['identifier']
        except:
            try:
                isbn = bookData['items'][0]['industryIdentifiers'][0]['identifier']
            except:
                try:
                    isbn = bookData['items'][0]['id']
                except:
                    isbn = ""

        title = bookData['items'][0]['volumeInfo']['title']
        try:
            authors = ""
            for item in bookData['items'][0]['volumeInfo']['authors']:
                authors += item + ","
        except:
            authors = ""
        try:
            year = bookData['items'][0]['volumeInfo']['publishedDate']
        except:
            year = ""
        try:
            publisher = bookData['items'][0]['volumeInfo']['publisher']
        except:
            publisher = ""
        try:
            image = bookData['items'][0]['volumeInfo']['imageLinks']['thumbnail']
        except:
            image = ""
        try:
            subtitle = bookData['items'][0]['volumeInfo']['subtitle']
        except:
            subtitle = ""
        try:
            desc = bookData['items'][0]['volumeInfo']['description']
        except:
            desc = ""
        categories = ""
        try:
            for item in bookData['items'][0]['volumeInfo']['categories']:
                categories += item + ","
        except:
            categories = ""
        try:
            previewLink = bookData['items'][0]['volumeInfo']['previewLink']
        except:
            previewLink = ""

        res = cur.execute('''SELECT isbn FROM books_metadata WHERE book_title = (?)''', [title]).fetchall()
        if(len(res) != 0):
            rating = cur.execute('''SELECT rating FROM book_rating WHERE isbn = (?) AND user_id = (?)''', [res[0][0], userId]).fetchall()
            if(len(rating) == 0):
                rating = -1
            else:
                rating = rating[0][0]
        else:
            rating = -1
        return [isbn,title,authors,year,publisher,image,subtitle,desc,categories,previewLink,float(rating)]


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

    def addBookRatingToDb(self, user_id, isbn, rating, bookName): #Done
        con = self.__connectToDB()
        cur = con.cursor()
        res = cur.execute('''SELECT isbn FROM books_metadata WHERE book_title = (?) AND isbn = (?)''', [bookName, isbn]).fetchall()
        if(len(res) == 0):
            urlQueryText = isbn
            api = "https://www.googleapis.com/books/v1/volumes?q=" + urlQueryText +"&maxResults=1"
            resp = urlopen(api)
            book_data = json.load(resp)
            book = BooksModel(self.__extractBookDetails(book_data, user_id))
            cur.execute('''INSERT INTO books_metadata values (?,?,?,?,?,?,?)''', [book.isbn, book.book_title, book.book_author, book.year_of_publication, book.publisher, book.image_url, book.categories])
            con.commit()
        try:
            cur.execute('''INSERT INTO book_rating VALUES (?,?,?)''', [user_id, isbn, rating])
            con.commit()
            con.close()
            return True
        except:
            con.close()
            return False

    def getBookBasedRecommendation(self, bookId):
        urlQueryText = bookId
        api = "https://www.googleapis.com/books/v1/volumes?q=" + urlQueryText +"&maxResults=1"
        resp = urlopen(api)
        book_data = json.load(resp)
        book = BooksModel(self.__extractBookDetails(book_data, -1))
        simAuth = self.__getSimilarAuthorBooks(book.book_author)
        simCat = self.__getSimilarCategoryBooks(book.categories)
        return json.dumps(simAuth + simCat, default=SectionModel.to_dict)

    def __getSimilarAuthorBooks(self, bookAuthors):
        secList = []
        for author in bookAuthors.split(','):
            if(author != ""):
                urlQueryText = author
                modQuery = urllib.parse.quote_plus(urlQueryText)
                api = "https://www.googleapis.com/books/v1/volumes?q=inauthor:" + modQuery +"&maxResults=40"
                resp = urlopen(api)
                book_data = json.load(resp)
                secList.append(SectionModel("Works By " + author, self.__extractBookListResponse(book_data)))
        return secList

    def __getSimilarCategoryBooks(self, bookCat):
        secList = []
        urlQueryText = bookCat
        modQuery = urllib.parse.quote_plus(urlQueryText)
        api = "https://www.googleapis.com/books/v1/volumes?q=subject:" + modQuery +"&maxResults=40"
        resp = urlopen(api)
        book_data = json.load(resp)
        secList.append(SectionModel(bookCat.replace(',', '') + " Books", self.__extractBookListResponse(book_data)))
        return secList

    def __getSimilarNameBooks(self, bookName):
        secList = []
        urlQueryText = bookName
        modQuery = urllib.parse.quote_plus(urlQueryText)
        api = "https://www.googleapis.com/books/v1/volumes?q=intitle:" + modQuery +"&maxResults=40"
        resp = urlopen(api)
        book_data = json.load(resp)
        secList.append(SectionModel("See Also", self.__extractBookListResponse(book_data)))
        return secList

    async def getHomePageBooks(self, userId):
        secList = []
        randomGenresList = self.__getRandomGenres()

        bestSellers = self.__getBestSellers()

        asyncio.set_event_loop(asyncio.new_event_loop())
        genresBookList = self.__getGenresSections(randomGenresList)

        secList.append(SectionModel("Best Sellers", bestSellers))
        return json.dumps(secList + genresBookList, default=SectionModel.to_dict)

    def searchForBook(self, query=""):
        urlQueryText = query.replace(' ', '+')
        api = "https://www.googleapis.com/books/v1/volumes?q=" + urlQueryText +"&maxResults=40"
        try:
            resp = urlopen(api)
        except:
            modQuery = urllib.parse.quote_plus(urlQueryText)
            api = "https://www.googleapis.com/books/v1/volumes?q=" + modQuery +"&maxResults=40"
            resp  = urlopen(api)
        book_data = json.load(resp)
        return json.dumps(self.__extractBookListResponse(book_data))


    def __getBestSellers(self):
        urlQueryText = "best selling books in usa".replace(' ', '+')
        urlParams = urllib.parse.quote_plus(urlQueryText)
        api = "https://www.googleapis.com/books/v1/volumes?q=" + urlParams +"&maxResults=40&startIndex="+ str(randrange(0, 50))
        resp = urlopen(api)
        book_data = json.load(resp)
        return self.__extractBookListResponse(book_data)

    def __getGenresSections(self, genreList):
        exList = []
        secList = []
        for genre in genreList:
            urlQueryText = "subject:"+genre.replace(' ','+').replace('&', '').replace('|', '')
            api = "https://www.googleapis.com/books/v1/volumes?q=" + urlQueryText +"&maxResults=40&startIndex="+ str(randrange(0, 50))
            try:
                resp = urlopen(api)
            except:
                modQuery = urllib.parse.quote_plus(urlQueryText)
                api = "https://www.googleapis.com/books/v1/volumes?q=" + modQuery +"&maxResults=40&startIndex="+ str(randrange(0, 50))
                resp = urlopen(api)
            book_data = json.load(resp)
            x = SectionModel("Popular " + genre.replace('|','') +" Books", self.__extractBookListResponse(book_data))
            exList.append(x)
        for exe in exList:
            if len(exe.itemList)> 0:
                secList.append(exe)
        return secList

    def __getGenreBooks(self, genre):
        urlQueryText = "subject:"+genre.replace(' ','+').replace('&', '').replace('|', '')
        api = "https://www.googleapis.com/books/v1/volumes?q=" + urlQueryText +"&maxResults=40&startIndex="+ str(randrange(0, 50))
        try:
            resp = urlopen(api)
        except:
            modQuery = urllib.parse.quote_plus(urlQueryText)
            api = "https://www.googleapis.com/books/v1/volumes?q=" + modQuery +"&maxResults=40&startIndex="+ str(randrange(0, 50))
            resp = urlopen(api)
        book_data = json.load(resp)
        return SectionModel("Popular " + genre.replace('|','') +" Books", self.__extractBookListResponse(book_data))

    def __getRandomGenres(self):
        con = self.__connectToDB()
        cur = con.cursor()
        all_genres = cur.execute('''SELECT genre_name FROM book_genres''').fetchall()
        shuffle(all_genres)
        gList = []
        i = 0
        for genre in all_genres:
            if i > 5:
                break
            gList.append(genre[0].replace('|',''))
            i += 1
        return gList


    def __extractBookListResponse(self, res):
        bList = []
        try:
            for book in res["items"]:
                try:
                    bId = book['id']
                except:
                    bId = ""
                try:
                    bTitle = str(book['volumeInfo']['title'])
                except:
                    bTitle = ""
                try:
                    bImage = book['volumeInfo']['imageLinks']['thumbnail']
                except:
                    bImage = ""
                bType = "book"
                bList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(bId, bTitle, bImage, bType)))
        except:
            bList = []
        return bList
