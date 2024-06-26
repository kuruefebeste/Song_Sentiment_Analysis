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
    return response.json()['label']


def create_song_data(songs):

    song_data = []
    for song in songs:
        song_title = song['title']
        sentiment = sentiment_analysis(song_title)
        song_data.append({'title': song_title,
                        'sentiment': sentiment})
    return song_data
        
artist_name = input("Enter the name of an artist: ")
artist_id = get_artist_id(artist_name)

artist_songs = get_artist_songs(artist_id)

song_data = create_song_data(artist_songs)

songs_df = pd.DataFrame(song_data)

engine = db.create_engine('sqlite:///songs.db')
songs_df.to_sql('user', con=engine, if_exists='replace', index=False)

with engine.connect() as connection:
   query_result = connection.execute(db.text("SELECT * FROM user;")).fetchall()
   print(pd.DataFrame(query_result))


## quick test edit