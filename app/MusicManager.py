from concurrent.futures.thread import ThreadPoolExecutor
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from app.SpotifyCredintials import Credintials as spcred
from app.InterestsRecommender.MusicRecommender import SongRecommender
import sqlite3
import json
from app.ProjectModels import SongModel, GenreModel
from app.ProjectModels import SongArtistModel
from app.ProjectModels import MediaItemPartialModel
from app.ProjectModels import SectionModel
import urllib.request
import urllib.parse
from urllib.request import Request
from bs4 import BeautifulSoup
import re
from random import shuffle
from random import randrange
from app.UserManager import UserManager as userManager
from app import TranslationManager as translator

client_credentials_manager = SpotifyClientCredentials(client_id=spcred.CLIENT_ID,
                                                      client_secret=spcred.CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


class MusicManager():
    def __connectToDB(self):
        con = sqlite3.connect(
            "app/pim_database.db")
        return con

    async def getHomePageSongs(self, userId, lang):
        with ThreadPoolExecutor(max_workers=8) as executor:
            resList = []
            resListOrdered = []
            userArtistrec = executor.submit(self.__getUserArtistSongsSpotifyRecommendation, userId)
            userGenreRecs = executor.submit(self.__getUserGenreSongsSpotifyRecommendation, userId)
            spotifyNewReleases = executor.submit(self.__getSpotifyNewReleases, lang)
            spotifyArtistRecommendation = executor.submit(self.__getUserArtistRecommendation, userId)
            userArtistTopSongs = executor.submit(self.__getUserArtistSongs, userId)
            userPlayedSongs = executor.submit(self.__getUserPlayedSongs, userId)
            userSongBasedRecommendation = executor.submit(self.__userSongBasedRecommendation, userId)
            userMoviesBasedRecommendation = executor.submit(self.__getMoviesBasedRecommendation, userId)

            songBasedRec = SectionModel(translator.getTranslationFor("Spotify Song Recommendations", lang),
                                        userSongBasedRecommendation.result())
            if len(songBasedRec.itemList) > 0:
                resList.append(songBasedRec)

            userSongs = SectionModel(translator.getTranslationFor("Quick Picks", lang), userPlayedSongs.result())
            if len(userSongs.itemList) > 0:
                resListOrdered.append(userSongs)

            artistSongs = SectionModel(translator.getTranslationFor("Songs From Your Favourite Artists", lang),
                                       userArtistTopSongs.result())
            if (len(artistSongs.itemList) > 0):
                resList.append(artistSongs)

            basedonArtist = SectionModel(translator.getTranslationFor("Based On The Artists You Like", lang),
                                         userArtistrec.result())
            if (len(basedonArtist.itemList) > 0):
                resList.append(basedonArtist)

            artistRecommendation = SectionModel(translator.getTranslationFor("Artists You May Like", lang),
                                                spotifyArtistRecommendation.result())
            if (len(artistRecommendation.itemList) > 0):
                resList.append(artistRecommendation)

            genreRecommendation = SectionModel(translator.getTranslationFor("Based on Genres You Liked", lang),
                                               userGenreRecs.result())
            if (len(genreRecommendation.itemList) > 0):
                resList.append(genreRecommendation)

            for rec in spotifyNewReleases.result():
                resList.append(SectionModel(rec[0], rec[1]))

            movieRecommendation = SectionModel(translator.getTranslationFor("Based on Movies You Liked", lang),
                                               userMoviesBasedRecommendation.result())
            if (len(movieRecommendation.itemList) > 0):
                resList.append(movieRecommendation)

            shuffle(resList)

            return json.dumps(resListOrdered + resList, default=SectionModel.to_dict)

    def findSongById(self, songSpotifyId):
        con = self.__connectToDB()
        cur = con.cursor()
        cur.execute(''' SELECT * FROM songs_metadata WHERE song_spotify_id = (?)''', [songSpotifyId])
        song = cur.fetchall()
        if len(song) != 0:

            album = cur.execute(''' SELECT * FROM music_albums WHERE album_spotify_id = (?)''', [song[0][1]]).fetchall()

            artistIds = str(song[0][2]).split(',')
            artistList = self.__findSongArtistsData(artistIds)
            ytID = self.__findSongYoutubeId2(song[0][4], artistList[0]['artist_name'])
            return json.dumps(SongModel(ytID, album[0][2], artistList, song[0]), default=SongModel.to_dict)
        else:
            return json.dumps(self.__findSpotifySongById(songSpotifyId), default=SongModel.to_dict)

    def getTopSongArtists(self):
        con = self.__connectToDB()
        res = []
        cur = con.cursor()
        recs = cur.execute(
            ''' SELECT artist_spotify_id, artist_name, image FROM song_artists ORDER BY popularity DESC LIMIT 100''').fetchall()
        for rec in recs:
            res.append(MediaItemPartialModel(rec[0], rec[1], rec[2], "artist"))
        return json.dumps(res, default=MediaItemPartialModel.to_dict)

    def getSongGenres(self):
        con = self.__connectToDB()
        res = []
        cur = con.cursor()
        recs = cur.execute(''' SELECT genre_name FROM songs_genres ORDER BY genre_name''').fetchall()
        for rec in recs:
            res.append(GenreModel(rec[0]))
        return json.dumps(res, default=GenreModel.to_dict)

    def searchForSong(self, query):
        spotifyResList = self.__searchInSpotify(query)
        return json.dumps(spotifyResList, default=MediaItemPartialModel.to_dict)

    def addSonglistening(self, userId, songId):
        con = self.__connectToDB()
        cur = con.cursor()
        try:
            playing_times = cur.execute(
                '''SELECT playing_times FROM user_song_listening WHERE user_id = (?) AND song_id =(?) ''',
                [userId, songId]).fetchall()
            if len(playing_times) == 0:
                cur.execute('''INSERT INTO user_song_listening values(?,?,?)''', [userId, songId, 1])
            else:
                playingtime = playing_times[0][0] + 1
                cur.execute(
                    '''UPDATE user_song_listening SET playing_times = (?) WHERE user_id = (?) AND song_id = (?) ''',
                    [playingtime, userId, songId])
            con.commit()
            con.close()
            return True
        except:
            return False

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
            songYtId = self.__findSongYoutubeId2(songName=tName, artistName=track['artists'][0]['name'])
        except:
            songYtId = ""

        print(songYtId)

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

    def __findSongYoutubeId2(self, songName="", artistName=""):
        artistName = artistName.replace(' ', '-').lower()
        songName = songName.replace(' ', '-').replace('/',' ').lower()
        urlSongName = ""
        i = 0
        for word in songName.split(' '):
            if i == 4:
                break
            urlSongName += word
            if i != 3 and i != len(songName.split(' ')) - 1:
                urlSongName += "-"
            i += 1
        urlParams = urllib.parse.quote_plus(artistName + "-" + urlSongName + "-" + "song")
        song_url = "https://watch.sm3na.org/" + urlParams + "/"
        print(song_url)
        with urllib.request.urlopen(Request(song_url, headers={'User-Agent': 'Mozilla/5.0'})) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            ytID = soup.find('input', id='videoId1')['value']
            return ytID

    def __extractSongForDatabase(self, track):
        tName = track['name']
        tId = track['id']
        tDuration = track['duration_ms']
        tArtists = ""
        tSpotifyLink = track['external_urls']['spotify']
        tAlbum = track['album']['id']
        for artist in track['artists']:
            tArtists += artist['id'] + ","
        songData = sp.audio_features([tId])
        try:
            tDanceability = songData[0]['danceability']
        except:
            tDanceability = 0.0
        try:
            tEnergy = songData[0]['energy']
        except:
            tEnergy = 0.0
        try:
            tLoudness = songData[0]['loudness']
        except:
            tLoudness = 0.0
        try:
            tTempo = songData[0]['tempo']
        except:
            tTempo = 0.0
        rec = [tId, tAlbum, tArtists, tDuration, tName, tSpotifyLink, tDanceability, tEnergy, tLoudness, tTempo]
        return rec

    def getSongBasedRecommendation(self, trackId, lang):
        con = self.__connectToDB()
        cur = con.cursor()
        secList = []
        retTrackRec = sp.recommendations(seed_tracks=[trackId])
        secList.append(SectionModel(translator.getTranslationFor("You May Also Like", lang),
                                    self.__extractSpotifyRecommendationResponse(retTrackRec)))

        track = sp.track(track_id=trackId)
        rec = self.__extractSongForDatabase(track)

        try:
            cur.execute(
                '''INSERT INTO songs_metadata (song_spotify_id, album_spotify_id, artists_spotify_id, duration, title, spotify_link, danceability, energy, loudness, tempo) VALUES (?,?,?,?,?,?,?,?,?,?)''',
                rec)
        except:
            print("error")

        artList = []
        for artist in track['artists']:
            artList.append(artist['id'])
        aData = self.__findSongArtistsData(artList)

        localRec = SongRecommender().ContentWithSongId(trackId, con)
        retLocalRec = sp.tracks(localRec)
        secList.append(
            SectionModel(translator.getTranslationFor("Hobbitor Recommendations", lang),
                         self.__extractSpotifyRecommendationResponse(retLocalRec)))

        if len(aData) > 0:
            try:
                seclist2 = self.__getAllArtistsRecommendation(aData, lang)
                return json.dumps(secList + seclist2, default=SectionModel.to_dict)
            except:
                pass
        else:
            return json.dumps(secList, default=SectionModel.to_dict)

    def __getMoviesBasedRecommendation(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        movieIds = cur.execute(
            '''SELECT movie_id FROM movie_rating WHERE user_id = (?) AND rating >= 4 ORDER BY rating''',
            [userId]).fetchall()
        if len(movieIds) == 0:
            return []
        sList = []
        for mId in movieIds:
            try:
                name = cur.execute('''SELECT title FROM movies_metadata WHERE movie_id = (?)''', [mId[0]]).fetchone()[0]
            except:
                continue
            if name != None:
                searchNameRes = sp.search(name, limit=5, offset=randrange(0, 3), type='track')
                results = []
                for song in searchNameRes["tracks"]["items"]:
                    tId = song["id"]
                    tName = song["name"]
                    try:
                        tAlbumImg = song['album']['images'][0]['url']
                    except:
                        tAlbumImg = ""
                    type = "song"
                    results.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(tId, tName, tAlbumImg, type)))
                if (len(results) > 0):
                    sList = sList + results
        shuffle(sList)
        return sList

    def __getAllArtistsRecommendation(self, artistList, lang):
        secList = []
        for artist in artistList:
            res = sp.artist_top_tracks(artist['artist_spotify_id'])
            secList.append(
                SectionModel(translator.getTranslationFor(artist['artist_name'] + " Top Songs", lang),
                             self.__extractSpotifyRecommendationResponse(res)))

        if len(artistList) > 1:
            randIdx = randrange(0, len(artistList) - 1)
        else:
            randIdx = 0
        simArtistsRes = sp.artist_related_artists(artistList[randIdx]['artist_spotify_id'])
        secList.append(SectionModel(translator.getTranslationFor("Artists Like ", lang) + artistList[randIdx]['artist_name'],
                                    self.__extractSpotifyArtistResponse(simArtistsRes)))
        return secList

    def __findSongArtistsData(self, artistList):
        alist = []
        for artistsId in artistList:
            try:
                if artistsId != "":
                    artist = sp.artist(artistsId)
                    rec = [artist['name'], artistsId, artist['images'][0]['url'], artist['followers']['total'],
                           artist['popularity'], artist['external_urls']['spotify']]
                    alist.append(SongArtistModel.to_dict(SongArtistModel(rec)))
            except:
                return []
        return alist

    def __getUserArtistSongsSpotifyRecommendation(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userArtists = cur.execute('''SELECT liked_song_artists FROM app_user WHERE user_id = (?)''',
                                  [userId]).fetchall()
        if (len(userArtists) > 0):
            artists = str(userArtists[0][0]).split(',')
            artistList = []

            randIdx = [*range(0, len(artists) - 1)]
            shuffle(randIdx)
            if (len(randIdx) > 4):
                randIdx = randIdx[:5]

            idList = []
            for songIdx in randIdx:
                idList.append(artists[songIdx])

            for artist in idList:
                if artist != "":
                    artistList.append(artist)
            try:
                retartistRec = sp.recommendations(seed_artists=artistList, limit=50)
            except:
                return []
            return self.__extractSpotifyRecommendationResponse(retartistRec)
        else:
            return []

    def __getUserGenreSongsSpotifyRecommendation(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userGenres = cur.execute('''SELECT liked_song_genre FROM app_user WHERE user_id = (?)''',
                                 [userId]).fetchall()
        if len(userGenres) > 0:
            genres = str(userGenres[0][0]).split(',')
            resList = []
            seedGenres = []
            for genre in genres:
                if genre != "":
                    seedGenres.append(genre)
            try:
                retgenreRec = sp.recommendations(seed_genres=seedGenres, limit=50, offset=randrange(0, 100))
            except:
                return []
            return self.__extractSpotifyRecommendationResponse(retgenreRec)
        else:
            return []

    def __getUserArtistRecommendation(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userGenres = cur.execute('''SELECT liked_song_artists FROM app_user WHERE user_id = (?)''',
                                 [userId]).fetchall()
        if (len(userGenres) > 0):
            artists = str(userGenres[0][0]).split(',')
            artist = artists[randrange(0, len(artists) - 2)]
            if artist != "":
                retArtist = sp.artist_related_artists(artist)
                return self.__extractSpotifyArtistResponse(retArtist)
            else:
                return []
        else:
            return []

    def __getSpotifyNewReleases(self, lang):
        retList = []
        newRel = sp.new_releases(limit=50, offset=randrange(0, 70))
        albums = []
        for item in newRel['albums']['items']:
            albums.append(item)

        retAlbumList = []
        for album in albums:
            retAlbumList.append(self.__extractAlbumData(album))
        retList.append((translator.getTranslationFor("New Albums", lang), retAlbumList))
        return retList

    def __getUserArtistSongs(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userArtists = cur.execute('''SELECT liked_song_artists FROM app_user WHERE user_id = (?)''',
                                  [userId]).fetchall()

        if len(userArtists) > 0:
            artists = str(userArtists[0][0]).split(',')
            try:
                artist = artists[randrange(0, len(artists) - 2)]
            except:
                return []
            res = sp.artist_top_tracks(artist)
            return self.__extractSpotifyRecommendationResponse(res)
        else:
            return []

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
        nameList = []
        trackList = []
        for track in res['tracks']:
            tId = track['id']
            tName = track['name']

            try:
                tAlbumImg = track['album']['images'][0]['url']
            except:
                tAlbumImg = ""
            if (tName not in nameList):
                trackList.append(MediaItemPartialModel.to_dict(MediaItemPartialModel(tId, tName, tAlbumImg, "song")))
                nameList.append(tName)
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
        userSongs = cur.execute(
            '''SELECT song_id FROM user_song_listening WHERE user_id = (?) AND playing_times >= 3 ORDER BY playing_times DESC''',
            [userId]).fetchall()

        if len(userSongs) > 0:
            shuffle(userSongs)
            idList = []
            for songId in userSongs:
                idList.append(songId[0])
            tracks = sp.tracks(idList)
            return self.__extractSpotifyRecommendationResponse(tracks)
        else:
            return []

    def __userSongBasedRecommendation(self, userId):
        con = self.__connectToDB()
        cur = con.cursor()
        userSongs = cur.execute('''SELECT song_id FROM user_song_listening WHERE user_id = (?)''',
                                [userId]).fetchall()

        if len(userSongs) > 0:
            if (len(userSongs) == 1):
                randIdx = [0]
            else:
                randIdx = [*range(0, len(userSongs) - 1)]
                shuffle(randIdx)

            if (len(randIdx) > 4):
                randIdx = randIdx[:5]

            idList = []
            for songIdx in randIdx:
                idList.append(userSongs[songIdx][0])
            tracks = sp.recommendations(seed_tracks=idList)
            return self.__extractSpotifyRecommendationResponse(tracks)
        else:
            return []

    def __searchInSpotify(self, query):
        resList = []
        res = sp.search(query, limit=50, offset=0, type="track,artist")
        for song in res["tracks"]["items"]:
            tId = song["id"]
            tName = song["name"]
            try:
                tAlbumImg = song['album']['images'][0]['url']
            except:
                tAlbumImg = ""
            type = "song"
            resList.append(MediaItemPartialModel(tId, tName, tAlbumImg, type))

        try:
            for artist in res["artists"]["items"]:
                aId = artist['id']
                aName = artist['name']
                try:
                    aImage = artist['images'][0]['url']
                except:
                    aImage = ""
                aType = "artist"
                resList.append(MediaItemPartialModel(aId, aName, aImage, aType))
        except:
            pass
        return resList

    def addUserLocalMusic(self, userId, songs=[]):
        con = self.__connectToDB()
        cur = con.cursor()
        try:
            plId = cur.execute('''SELECT playlist_id FROM user_playlists WHERE playlist_name = (?)''',
                               ["My Local Music"]).fetchall()[0][0]
            if plId == None:
                userManager().createPlaylist(userId, "My Local Music", "music")
                plId = cur.execute('''SELECT playlist_id FROM user_playlists WHERE playlist_name = (?)''',
                                   ["My Local Music"]).fetchall()[0][0]
        except:
            userManager().createPlaylist(userId, "My Local Music", "music")
            plId = cur.execute('''SELECT playlist_id FROM user_playlists WHERE playlist_name = (?)''',
                               ["My Local Music"]).fetchall()[0][0]
        con.close()
        for song in songs:
            res = sp.search(song, limit=1, offset=0, type="track")
            try:
                for song in res["tracks"]["items"]:
                    tId = song["id"]
                    tName = song["name"]
                    try:
                        tAlbumImg = song['album']['images'][0]['url']
                    except:
                        tAlbumImg = ""
                    artistList = []
                    try:
                        for artist in song["album"]["artists"]:
                            artistList.append(artist["id"])
                            self.__addUserArtistPref(userId, artist["id"])
                    except:
                        artistList = []
                    self.__addItemToMusicPlaylist(plId, tId, tName, tAlbumImg)
                    self.__setUserSongListening(userId, tId)
            except:
                continue
        return True

    def __addItemToMusicPlaylist(self, plId, itemId, itemName, itemImage):
        userManager().addPlaylistItem(plId, itemId, itemName, itemImage)

    def __addUserArtistPref(self, userId, artistId):
        con = self.__connectToDB()
        cur = con.cursor()
        userArtists = str(cur.execute('''SELECT liked_song_artists FROM app_user WHERE user_id = (?)''',
                                      [userId]).fetchall()[0][0])
        if not artistId in userArtists:
            userArtists += artistId + ","
        cur.execute('''UPDATE app_user SET liked_song_artists = (?) WHERE user_id = (?)''', [userArtists, userId])
        con.commit()
        con.close()

    def __setUserSongListening(self, userId, songId):
        con = self.__connectToDB()
        cur = con.cursor()
        try:
            playing_times = cur.execute(
                '''SELECT playing_times FROM user_song_listening WHERE user_id = (?) AND song_id =(?) ''',
                [userId, songId]).fetchall()
            if len(playing_times) == 0:
                cur.execute('''INSERT INTO user_song_listening values(?,?,?)''', [userId, songId, 3])
            else:
                playingtime = playing_times[0][0] + 2
                cur.execute(
                    '''UPDATE user_song_listening SET playing_times = (?) WHERE user_id = (?) AND song_id = (?) ''',
                    [playingtime, userId, songId])
            con.commit()
            con.close()
        except:
            return
