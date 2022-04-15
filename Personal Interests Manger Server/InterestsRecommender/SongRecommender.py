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
        df["sum"]=df["danceability"]+df["energy"]+df["loudness"]+df["tempo"]
        df2["sum"]=df2["danceability"]+df2["energy"]+df2["loudness"]+df2["tempo"]
        df["sum"]=df["sum"].astype(float)
        df2["sum"]=df2["sum"].astype(float)
        x=df2["sum"].values
        df["sum"]=abs(df["sum"]-x)
        df=df.sort_values(by="sum", ascending=True)
        return df['song_id']


r=Song()
print(r.ContentWithSongId(56))
#56