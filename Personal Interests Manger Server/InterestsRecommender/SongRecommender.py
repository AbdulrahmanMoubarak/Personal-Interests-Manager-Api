import pandas as pd
import sqlite3


class SongRecommender:

    def ContentWithSongId(self, SongId, conn):
        df = pd.read_sql_query("""SELECT song_spotify_id, danceability, energy, loudness, tempo FROM songs_metadata""",
                               conn)
        df2 = pd.read_sql_query(
            """SELECT song_spotify_id, danceability, energy, loudness, tempo FROM songs_metadata WHERE song_spotify_id=(?)""", conn, params=[SongId])
        return self.__ContentBased(df, df2)

    def __ContentBased(self, df, df2):
        df["tempo"] = abs(abs(df["tempo"]) - abs(df2["tempo"].values))
        df["energy"] = abs(abs(df["energy"]) - abs(df2["energy"].values))
        df["danceability"] = abs(abs(df["danceability"]) - abs(df2["danceability"].values))
        df["loudness"] = abs(abs(df["loudness"]) - abs(df2["loudness"].values))
        df = df.sort_values(by=["tempo", "energy", "danceability", "loudness"], ascending=True)
        subDf = df.loc[(df['tempo'] > float(0)) | (df['energy'] > float(0)) | (df['danceability'] > float(0)) | (df['loudness'] > float(0))]
        ret = subDf['song_spotify_id'].tolist()
        return ret[:40]
