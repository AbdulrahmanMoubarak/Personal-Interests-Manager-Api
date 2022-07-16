import json
import re
import sqlite3
from flask import jsonify

from app.ProjectModels import UserModel, MediaItemPartialModel


class UserManager():
    def __connectToDB(self):
        con = sqlite3.connect(
            "app/pim_database.db")
        return con

    def registerUser(self, email, password, username):
        con = self.__connectToDB()
        cursor = con.cursor()
        try:
            cursor.execute("INSERT INTO app_user (name, email, password) VALUES (?,?,?)", [username, email, password])
            con.commit()
            con.close()
            return True
        except:
            con.close()
            return False

    def addUserPreferences(self, favArtists, favSongGenres, email):
        con = self.__connectToDB()
        cursor = con.cursor()
        try:
            cursor.execute("UPDATE app_user SET (liked_song_artists, liked_song_genre) = (?,?) WHERE email = (?)",
                           [favArtists, favSongGenres, email])
            con.commit()
            con.close()
            return True
        except:
            con.close()
            return False

    def login(self, email, password):
        con = self.__connectToDB()
        cursor = con.cursor()
        res = cursor.execute("SELECT * FROM app_user WHERE email = (?)", [email]).fetchall()
        print("len = " + str(len(res)))
        if (len(res) == 0):
            return jsonify({"message": "wrong data"}), 404
        else:
            resPass = res[0][3]
            if password != resPass:
                return jsonify({"message": "wrong data"}), 404
            else:
                return json.dumps(UserModel(res[0][0], res[0][1], res[0][2]), default=UserModel.to_dict)

    def createPlaylist(self, userId, PlaylistName, PlaylistType):
        db = self.__connectToDB()
        cursor = db.cursor()
        if (userId != None and PlaylistName != None and PlaylistType != None):
            cursor.execute(
                'INSERT INTO user_playlists (user_id,playlist_name,playlist_type,playlist_image) VALUES(?,?,?,?)',
                [userId, PlaylistName, PlaylistType, ""])
            db.commit()
            db.close()
            return True
        else:
            db.close()
            return False

    def addPlaylistItem(self, PlaylistId, itemId, itemName, itemImage):
        db = self.__connectToDB()
        cursor = db.cursor()
        res = cursor.execute('''SELECT * FROM playlist_items WHERE playlist_id = (?) AND item_id = (?)'''
                             , [PlaylistId, itemId]).fetchall()
        if len(res) != 0:
            db.close()
            return False
        if PlaylistId != None and itemId != None and itemName != None and itemImage != None:
            try:
                cursor.execute('INSERT INTO playlist_items (playlist_id,item_id,item_name,item_image) VALUES(?,?,?,?)',
                               [PlaylistId, itemId, itemName, itemImage])
                db.commit()
                cursor.execute('''UPDATE user_playlists SET (playlist_image) = (?) WHERE playlist_id = (?)''',
                               [itemImage, PlaylistId])
                db.commit()
                db.close()
                return True
            except:
                return False
        else:
            db.close()
            return False

    def getAllPlaylists(self, userId):
        con = self.__connectToDB()
        cursor = con.cursor()
        pls = []
        recs = cursor.execute('''SELECT * FROM user_playlists WHERE user_id = (?)''', [userId]).fetchall()
        for rec in recs:
            pls.append(MediaItemPartialModel(rec[1], rec[2], rec[4], rec[3]))
        return json.dumps(pls, default=MediaItemPartialModel.to_dict)

    def getAllPlaylistsOfType(self, userId, type):
        con = self.__connectToDB()
        cursor = con.cursor()
        pls = []
        recs = cursor.execute('''SELECT * FROM user_playlists WHERE user_id = (?) AND playlist_type =(?)''',
                              [userId, type]).fetchall()
        for rec in recs:
            pls.append(MediaItemPartialModel(rec[1], rec[2], rec[3], rec[4]))
        return json.dumps(pls, default=MediaItemPartialModel.to_dict)

    def getUserPlaylistItems(self, playlistId):
        con = self.__connectToDB()
        cursor = con.cursor()
        plType = \
            cursor.execute('''SELECT playlist_type FROM user_playlists WHERE playlist_id = (?)''',
                           [playlistId]).fetchall()[
                0][0]
        pls = []
        recs = cursor.execute('''SELECT * FROM playlist_items WHERE playlist_id = (?)''', [playlistId]).fetchall()
        for rec in recs:
            pls.append(MediaItemPartialModel(rec[1], rec[2], rec[3], plType))
        return json.dumps(pls, default=MediaItemPartialModel.to_dict)
