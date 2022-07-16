from chatterbot.response_selection import get_random_response
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
from chatterbot import ChatBot
import pandas as pd
import sqlite3

conn = sqlite3.connect("pim_database.db")

chatbot = ChatBot("Ron Obvious")

# trainer = ChatterBotCorpusTrainer(chatbot)
# trainer.train('chatterbot.corpus.english.Recommend')

requests_list = []


class ChatBot:
    def Chat(self, request):
        requests_list.append(request)
        response = chatbot.get_response(request)
        if (requests_list[len(requests_list) - 2].lower() == "Movies".lower() or requests_list[
            len(requests_list) - 2].lower() == "recommend me a movie".lower() or requests_list[
            len(requests_list) - 2] == "افلام"):
            if len(request) != 0:
                df = pd.read_sql_query(
                    """Select genres,title from movies_metadata where genres LIKE '%""" + str(request) + """%'""", conn)
                if df.empty:
                    return "bot: Sorry couldnt Find anything"
                else:
                    return df

        elif (requests_list[len(requests_list) - 2].lower() == "Books".lower() or requests_list[
            len(requests_list) - 2] == "كتاب"):
            if len(request) != 0:
                df = pd.read_sql_query(
                    """Select book_title from books_metadata where book_author LIKE '%""" + str(request) + """%'""",
                    conn)
                if df.empty:
                    return "bot: Sorry couldnt Find anything"
                else:
                    return df

        elif (requests_list[len(requests_list) - 2].lower() == "Songs".lower() or requests_list[
            len(requests_list) - 2] == "اغاني"):
            if len(request) != 0:
                df = pd.read_sql_query(
                    """Select artist_name, artist_spotify_id from song_artists where artist_name LIKE '%""" + str(
                        request) + """%'""", conn)
                df2 = pd.read_sql_query("""Select title, artists_spotify_id from songs_metadata""", conn)
                df['artists_spotify_id'] = df['artist_spotify_id'].astype(str) + ','
                merged = pd.merge(df, df2)
                if merged.empty:
                    return "bot: Sorry couldnt Find anything"
                else:
                    return merged["title"]


        else:
            return "bot:" + str(response)
