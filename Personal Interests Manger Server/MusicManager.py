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

client_credentials_manager = SpotifyClientCredentials(client_id=spcred.CLIENT_ID,
                                                      client_secret=spcred.CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


class MusicManager():
    def __connectToDB(self):
        con = sqlite3.connect(
            "D:/FCIS SWE 2021/Graduation Project/Project source code/Dataset Migration/pim_database.db")
        return con

    def getHomePageSongs(self, userId):
        with ThreadPoolExecutor(max_workers=7) as executor:
            resList = []
            userArtistrec = executor.submit(self.__getUserArtistSongsSpotifyRecommendation, userId)
            userGenreRecs = executor.submit(self.__getUserGenreSongsSpotifyRecommendation, userId)
            spotifyNewReleases = executor.submit(self.__getSpotifyNewReleases)
            spotifyArtistRecommendation = executor.submit(self.__getUserArtistRecommendation, userId)
            userArtistTopSongs = executor.submit(self.__getUserArtistSongs, userId)
            userPlayedSongs = executor.submit(self.__getUserPlayedSongs, userId)
            userSongBasedRecommendation = executor.submit(self.__userSongBasedRecommendation, userId)

            songBasedRec = SectionModel("Spotify Song Recommendations", userSongBasedRecommendation.result())
            resList.append(songBasedRec)

            userSongs = SectionModel("Quick Picks", userPlayedSongs.result())
            resList.append(userSongs)

            artistSongs = SectionModel("Songs From Your Favourite Artists", userArtistTopSongs.result())
            resList.append(artistSongs)

            basedonArtist = SectionModel("Based On The Artists You Like", userArtistrec.result())
            resList.append(basedonArtist)

            artistRecommendation = SectionModel("Artists You May Like", spotifyArtistRecommendation.result())
            resList.append(artistRecommendation)

            resList.append(SectionModel("Based on Genres You Liked", userGenreRecs.result()))

            for rec in spotifyNewReleases.result():
                resList.append(SectionModel(rec[0], rec[1]))

            shuffle(resList)

            return json.dumps(resList, default=SectionModel.to_dict)

    def findSongById(self, songSpotifyId):
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute(''' SELECT * FROM songs_metadata WHERE song_spotify_id = (?)''', [songSpotifyId])
        song = cur.fetchall()
        if len(song) != 0:

            album = cur.execute(''' SELECT * FROM music_albums WHERE album_spotify_id = (?)''', [song[0][1]]).fetchall()

            artistIds = str(song[0][2]).split(',')
            artistList = self.__findSongArtistsData(artistIds)
            ytID = self.__findSongYoutubeId(song[0][4], artistList[0]['artist_name'])
            return json.dumps(SongModel(ytID, album[0][2], artistList, song[0]), default=SongModel.to_dict)
        else:
            return json.dumps(self.__findSpotifySongById(songSpotifyId), default=SongModel.to_dict)

    def __findSpotifySongById(self, songSpotifyId):
        track = sp.track(track_id=songSpotifyId)
        tName = track['name']
        tDuration = track['duration_ms']
        tArtists = ""
        artList = []
        tSpotifyLink = track['external_urls']['spotify']
        tAlbumId = track['album']['id']
        tAlbumImg = track['album']['images'][0]['url']
        for artist in track['artists']:
            tArtists += artist['id'] + ","
            artList.append(artist['id'])
        try:
            songYtId = self.__findSongYoutubeId(tName, track['artists'][0]['name'])
        except:
            songYtId = ""

        artists = self.__findSongArtistsData(artList)
        return SongModel(songYtId, tAlbumImg, artists,
                         [0, tAlbumId, tArtists, tDuration, tName, songSpotifyId, tSpotifyLink])

    def __findSongYoutubeId(self, songName, artistName):
        artistName = artistName.replace(' ', '-')
        songName = re.sub("['?}{:.;!@#%^&*(,)]", '', str(songName)).lower()
        urlSongName = ""
        i = 0
        for word in songName.split(' '):
            if i == 4:
                break
            urlSongName += word
            if i != 3:
                urlSongName += "-"
            i += 1
        movie_url = "https://" + artistName + "-" + urlSongName + ".mp3juices.icu"
        with urllib.request.urlopen(movie_url) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            ytID = soup.find('li', class_='playing')['yt']
            return ytID

    def __findSongArtistsData(self, artistList):
        alist = []
        for artistsId in artistList:
            if artistsId != "":
                artist = sp.artist(artistsId)
                rec = [artist['name'], artistsId, artist['images'][0]['url'], artist['followers']['total'],
                       artist['popularity'], artist['external_urls']['spotify']]
                alist.append(SongArtistModel.to_dict(SongArtistModel(rec)))
        return alist

    def __getUserArtistSongsSpotifyRecommendation(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userArtists = cur.execute('''SELECT liked_song_artists FROM app_user WHERE user_id = (?)''',
                                  [userId]).fetchall()[0]
        artists = str(userArtists[0]).split(',')
        artistList = []
        for artist in artists:
            if artist != "":
                artistList.append(artist)

        retartistRec = sp.recommendations(seed_artists=artistList, limit=50)
        return self.__extractSpotifyRecommendationResponse(retartistRec)

    def __getUserGenreSongsSpotifyRecommendation(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userGenres = cur.execute('''SELECT liked_song_genre FROM app_user WHERE user_id = (?)''',
                                 [userId]).fetchall()[0]
        genres = str(userGenres[0]).split(',')
        resList = []
        seedGenres = []
        for genre in genres:
            if genre != "":
                seedGenres.append(genre)
        retgenreRec = sp.recommendations(seed_genres=seedGenres, limit=50, offset=randrange(0, 100))
        # resList.append((genre, self.__extractSpotifyRecommendationResponse(retgenreRec)))

        return self.__extractSpotifyRecommendationResponse(retgenreRec)

    def __getUserArtistRecommendation(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userGenres = cur.execute('''SELECT liked_song_artists FROM app_user WHERE user_id = (?)''',
                                 [userId]).fetchall()[0]
        artists = str(userGenres[0]).split(',')
        artist = artists[randrange(0, len(artists) - 2)]
        if artist != "":
            retArtist = sp.artist_related_artists(artist)
            return self.__extractSpotifyArtistResponse(retArtist)
        else:
            return []

    def __getSpotifyNewReleases(self):
        retList = []
        newRel = sp.new_releases(limit=50, offset=randrange(0, 70))
        albums = []
        for item in newRel['albums']['items']:
            albums.append(item)

        retAlbumList = []
        for album in albums:
            retAlbumList.append(self.__extractAlbumData(album))
        retList.append(("New Albums", retAlbumList))
        return retList

    def __getUserArtistSongs(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userGenres = cur.execute('''SELECT liked_song_artists FROM app_user WHERE user_id = (?)''',
                                 [userId]).fetchall()[0]
        artists = str(userGenres[0]).split(',')
        artist = artists[randrange(0, len(artists) - 2)]
        res = sp.artist_top_tracks(artist)
        return self.__extractSpotifyRecommendationResponse(res)

    def __extractAlbumData(self, album):
        aId = album['id']
        aName = album['name']
        aImage = album['images'][0]['url']
        aType = "album"
        return MediaItemPartialModel.to_dict(MediaItemPartialModel(aId, aName, aImage, aType))

    # def __getTrackFromSpotifySingleAlbum(self, single):
    #     trackres = sp.album_tracks(album_id=single['id'], limit=1)
    #     sId = trackres['items'][0]['id']
    #     sName = trackres['items'][0]['name']
    #     sImage = single['images'][0]['url']
    #     sType = "song"
    #     return MediaItemPartialModel.to_dict(MediaItemPartialModel(sId, sName, sImage, sType))

    def __extractSpotifyRecommendationResponse(self, res):
        trackList = []
        for track in res['tracks']:
            tId = track['id']
            tName = track['name']
            try:
                tAlbumImg = track['album']['images'][0]['url']
            except:
                tAlbumImg = ""
            trackList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(tId, tName, tAlbumImg, "song")))
        return trackList

    def __extractArtistFromRecommendationResponse(self, artistList):
        alist = []
        for artist in artistList:
            rec = [artist['name'], artist['id'], artist['images'][0]['url'], artist['followers']['total'],
                   artist['popularity'], artist['external_urls']['spotify']]
            alist.append(SongArtistModel.to_dict(SongArtistModel(rec)))
        return alist

    def __extractSpotifyArtistResponse(self, res):
        artistList = []
        for artist in res['artists']:
            aId = artist['id']
            aName = artist['name']
            try:
                aImage = artist['images'][0]['url']
            except:
                aImage = ""
            aType = "artist"
            artistList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(aId, aName, aImage, aType)))
        shuffle(artistList)
        return artistList

    def __getUserPlayedSongs(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userSongs = cur.execute('''SELECT song_id FROM user_song_listening WHERE user_id = (?)''',
                                [userId]).fetchall()

        idList = []
        for songId in userSongs:
            idList.append(songId[0])
        tracks = sp.tracks(idList)
        shuffle(tracks)
        return self.__extractSpotifyRecommendationResponse(tracks)

    def __userSongBasedRecommendation(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userSongs = cur.execute('''SELECT song_id FROM user_song_listening WHERE user_id = (?)''',
                                [userId]).fetchall()

        idList = []
        for songId in userSongs:
            idList.append(songId[0])
        tracks = sp.recommendations(seed_tracks=idList)
        return self.__extractSpotifyRecommendationResponse(tracks)
