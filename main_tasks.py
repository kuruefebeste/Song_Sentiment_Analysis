import requests
import json
import sqlalchemy as db
import pandas as pd
import os
import lyricsgenius

# source: https://gist.github.com/imdkm/a60247b59ff1881fa4bb8846a9b44c96

CLIENT_ACCESS_TOKEN = os.environ.get("CLIENT_ACCESS_TOKEN")
BASE_URL = "https://api.genius.com"

genius = lyricsgenius.Genius(CLIENT_ACCESS_TOKEN)

def get_artist_id(name):
    '''
    This method returns the id of the artist_name given as a input.
    '''
    headers = {'Authorization': f'Bearer {CLIENT_ACCESS_TOKEN}'}
    requrl = '/'.join([BASE_URL, "search"])
    param = {'q': name}

    response = requests.get(requrl, headers=headers, params=param)
    response_json = response.json()

    if response_json["response"]:
        artist_info = response_json["response"]["hits"][0]["result"]["primary_artist"]
        return artist_info["id"]
    
    return "The artist cannot be found."

def get_artist_songs(artist_id):

    songs_response = genius.artist_songs(artist_id=artist_id, per_page=20, sort="popularity")
    songs = songs_response["songs"]
    return songs

def sentiment_analysis(text):

    sentiment_url = "http://text-processing.com/api/sentiment/"
    response = requests.post(sentiment_url, data={'text': text})
    response_json = response.json()
    return response_json.get("label", "neutral")


def create_song_data(artist_name, songs):

    song_data = []
    for song in songs:
        song_title = song['title']
        sentiment = sentiment_analysis(song_title)
        song_data.append({'artist_name': artist_name,
                        'song_title': song_title,
                        'sentiment': sentiment})
    return song_data
        
artist_names = []

# try ed sheeran and britney spears
for i in range(1):
    name = input("Enter the name of an artist: ")
    artist_names.append(name)

engine = db.create_engine('sqlite:///songs.db')

for artist_name in artist_names:
    artist_id = get_artist_id(artist_name)

    if artist_id:
        artist_songs = get_artist_songs(artist_id)
        song_data = create_song_data(artist_name,artist_songs)

        songs_df = pd.DataFrame(song_data)

        table_name = artist_name.replace(" ", "_").lower()

        songs_df.to_sql(table_name, con=engine, if_exists='replace', index=False)

        with engine.connect() as connection:
            query_result = connection.execute(db.text(f"SELECT * FROM {table_name};")).fetchall()
            result_df = pd.DataFrame(query_result, columns=['artist_name', 'song_title', 'sentiment'])
            print()
            print(f"Artist: {artist_name}")
            print(result_df)
            
            print()
            sentiment_summary_temp = result_df["sentiment"].value_counts(normalize=True)

            # transforms the indices to a regular column
            sentiment_summary = sentiment_summary_temp.reset_index()
            sentiment_summary.columns = ['sentiment', 'proportion']
            sentiment_summary_table_name = f"{table_name}_sentiment_summary"
            sentiment_summary.to_sql(sentiment_summary_table_name, con=engine, if_exists='replace', index=False)
            
            print(sentiment_summary)

            dominant_sentiments = sentiment_summary.nlargest(2, 'proportion')
            first_dominant_val = dominant_sentiments.iloc[0]['sentiment']
            second_dominant_val = dominant_sentiments.iloc[1]['sentiment']

            # makes the output print statement more readable
            sentiment_map = {"pos": "positive", "neg": "negative", "neutral": "neutral"}
            first_dominant = sentiment_map.get(first_dominant_val)
            second_dominant = sentiment_map.get(second_dominant_val)

            print()
            print(f"{artist_name} tends to come up with more {first_dominant}-{second_dominant} sounding song titles.")
       
    else:
        print("Artist cannot be found.")


