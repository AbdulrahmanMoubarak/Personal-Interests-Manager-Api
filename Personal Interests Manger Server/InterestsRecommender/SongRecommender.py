import pandas as pd
import sqlite3
conn = sqlite3.connect("pim_database.db")

class Song:

    def ContentWithSongId(self,SongId):
        conn = sqlite3.connect("pim_database.db")
        df = pd.read_sql_query("""Select song_id , danceability, energy,loudness,tempo from songs_metadata""", conn)
        df2 = pd.read_sql_query("""Select song_id , danceability, energy,loudness,tempo from songs_metadata where song_id="""+str(SongId), conn)
        return self.ContentBased(df,df2)

    def ContentBased(self,df,df2):
        df=abs(df)
        df2=abs(df2)
        df["tempo"]=abs(df["tempo"]-df2["tempo"].values)
        df["energy"]=abs(df["energy"]-df2["energy"].values)
        df["danceability"]=abs(df["danceability"]-df2["danceability"].values)
        df["loudness"]=abs(df["loudness"]-df2["loudness"].values)
        df=df.sort_values(by=["tempo","energy","danceability","loudness"], ascending=True)
        return df['song_id']


r=Song()
print(r.ContentWithSongId(56))
#56
