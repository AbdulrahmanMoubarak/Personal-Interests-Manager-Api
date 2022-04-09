from concurrent.futures.thread import ThreadPoolExecutor

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from SpotifyCredintials import Credintials as spcred
import sqlite3
import json
from ProjectModels import SongModel
from ProjectModels import SongArtistModel
from ProjectModels import MediaItemPartialModel
from ProjectModels import SectionModel
import urllib.request
from bs4 import BeautifulSoup
import re
from random import shuffle
from random import randrange
from flask import Flask, abort
class usersManger():
    def signUp(self,userId,userName,userEmail,userPassword):
        con = self.__connectToDB()
        cur = con.cursor()
        message=cur.execute('''SELECT userId from app_user WHERE email =(?)''',[userEmail],).fetchall()
        if len(message)==0 :
           cur.execute('''INSERT INTO app_user values(?,?,?,?)''',[userId,userName,userEmail,userPassword])
           con.close()
        else:
            return  abort(409)

    def addfavorites(self,userEmail,likedMovie,likedSongArtist,likedBook,likedSongGenre):
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute('''UPDATE app_user SET values(?,?,?,?) WHERE email=(?)''', [ likedMovie, likedSongArtist,likedBook,likedSongGenre,userEmail])
        con.close()