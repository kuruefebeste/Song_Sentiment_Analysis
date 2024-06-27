'''
Project Collaborators: Beste Kuruefe and Mercy Olagunju
Date: June 28, 2024

This file executes the main tasks of the Song Sentiment Analysis Project,
which is created as the Week 2 Project of the SEO Tech Developer Program.
'''


import requests
import json
import sqlalchemy as db
import pandas as pd
import os
import lyricsgenius


CLIENT_ACCESS_TOKEN = os.environ.get("CLIENT_ACCESS_TOKEN")

BASE_URL = "https://api.genius.com"

genius = lyricsgenius.Genius(CLIENT_ACCESS_TOKEN)


def get_artist_id(name):
    '''
    Returns the id of the artist_name given as an input.
    '''
    headers = {'Authorization': f'Bearer {CLIENT_ACCESS_TOKEN}'}
    requrl = '/'.join([BASE_URL, "search"])
    param = {'q': name}

    response = requests.get(requrl, headers=headers, params=param)
    response_json = response.json()

    if response_json["response"]:
        artist_info = response_json["response"]["hits"][0]["result"]
        artist_id_num = artist_info["primary_artist"]["id"]
        return artist_id_num

    return "The artist cannot be found."


def get_artist_songs(artist_id):
    '''
    Returns the songs of the artist, whose id is given as input.
    '''

    song_resp = genius.artist_songs(artist_id, per_page=20, sort="popularity")
    songs = song_resp["songs"]
    return songs


def sentiment_analysis(text):
    '''
    Performs a sentiment analysis on the text given as an input.
    Returns a json response, neutral being the default value.
    '''

    sentiment_url = "http://text-processing.com/api/sentiment/"
    response = requests.post(sentiment_url, data={'text': text})
    response_json = response.json()
    return response_json.get("label", "neutral")


def create_song_data(artist_name, songs):
    '''
    Creates and returns a song data list.
    '''

    song_data = []
    for song in songs:
        song_title = song['title']
        sentiment = sentiment_analysis(song_title)
        song_data.append({
            'artist_name': artist_name,
            'song_title': song_title,
            'sentiment': sentiment
        })
    return song_data


artist_names = []

# Asks the user for three artist names
for i in range(3):
    # Try ed sheeran, britney spears, justin timberlake
    name = input("Enter the name of an artist: ")
    artist_names.append(name)

# Creates an SQLite Database engine, which connects to the database named songs.db
engine = db.create_engine('sqlite:///songs.db')

for artist_name in artist_names:
    artist_id = get_artist_id(artist_name)

    if artist_id:
        artist_songs = get_artist_songs(artist_id)
        song_data = create_song_data(artist_name, artist_songs)

        songs_df = pd.DataFrame(song_data)

        # Creates a table name by replacing spaces with underscores and converting to lowercase
        # Example: 'Ed Sheeran' -> 'ed_sheeran'
        table_name = artist_name.replace(" ", "_").lower()

        songs_df.to_sql(table_name, con=engine, if_exists='replace', index=False)

        # Connects to the SQLite database
        with engine.connect() as connection:

            # Does a query to retrieve all rows from the table
            query_result = connection.execute(db.text(f"SELECT * FROM {table_name};")).fetchall()
            result_df = pd.DataFrame(query_result, columns=['artist_name', 'song_title', 'sentiment'])

            print()
            print(f"Artist: {artist_name}")
            print(result_df)
            print()

            # Calculates the proportion of each sentiment in the songs
            sentiment_summary_temp = result_df["sentiment"].value_counts(normalize=True)

            # Transforms the indices to a regular column
            sentiment_summary = sentiment_summary_temp.reset_index()

            sentiment_summary.columns = ['sentiment', 'proportion']
            sentiment_summary_table_name = f"{table_name}_sentiment_summary"
            sentiment_summary.to_sql(sentiment_summary_table_name, con=engine, if_exists='replace', index=False)

            print(sentiment_summary)
            
            # Determines the two most dominant sentiments
            dominant_sentiments = sentiment_summary.nlargest(2, 'proportion')
            first_dominant_val = dominant_sentiments.iloc[0]['sentiment']
            second_dominant_val = dominant_sentiments.iloc[1]['sentiment']

            # Makes the output print statement more readable
            sentiment_map = {"pos": "positive", "neg": "negative", "neutral": "neutral"}
            first_dominant = sentiment_map.get(first_dominant_val)
            second_dominant = sentiment_map.get(second_dominant_val)

            print()
            print(f"{artist_name} tends to come up with more {first_dominant}-{second_dominant} sounding song titles.")
       
    else:
        print("Artist cannot be found.")
