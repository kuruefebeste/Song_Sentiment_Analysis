"""
Author: Mercy Olagunju
Module providing a unittest functions.
"""

import unittest
from unittest.mock import patch
from main_tasks import (
    get_artist_id,
    create_song_data,
    sentiment_analysis,
    get_artist_songs,
)


class TestMusicAnalysisFunctions(unittest.TestCase):
    """Class testing functions in main_tasks"""

    @patch("requests.get")
    def test_get_artist_id_known_artist(self, mock_get):
        """test get_artist_id function"""
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            "response": {"hits": [{"result": {"primary_artist":
                                              {"id": 12345}}}]}
        }
        artist_id = get_artist_id("Adele")
        self.assertEqual(artist_id, 12345)

    @patch("requests.get")
    def test_get_artist_id_unknown_artist(self, mock_get):
        """test get_artist_id function"""
        mock_response = mock_get.return_value
        mock_response.json.return_value = {"response": []}
        artist_id = get_artist_id("Unknown Artist")
        self.assertEqual(artist_id, "The artist cannot be found.")

    @patch("main_tasks.sentiment_analysis")
    def test_create_song_data(self, mock_sentiment):
        """test create_song_data function"""
        mock_sentiment.side_effect = ["positive", "negative"]
        songs = [{"title": "Happy Song"}, {"title": "Sad Song"}]
        artist_name = "Adele"
        song_data = create_song_data(artist_name, songs)
        self.assertEqual(len(song_data), 2)
        self.assertEqual(song_data[0]["sentiment"], "positive")
        self.assertEqual(song_data[1]["sentiment"], "negative")

    @patch("requests.post")
    def test_sentiment_analysis_positive(self, mock_post):
        """test sentiment_analysis function"""
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {"label": "pos"}
        sentiment = sentiment_analysis("Another love song")
        self.assertEqual(sentiment, "pos")

    @patch("requests.post")
    def test_sentiment_analysis_network_error(self, mock_post):
        """test sentiment_analysis function"""
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {}
        sentiment = sentiment_analysis("I hate this song")
        self.assertEqual(sentiment, "neutral")  # should be default response

    @patch("main_tasks.lyricsgenius.Genius.artist_songs")
    def test_get_artist_songs_successful(self, mock_artist_songs):
        """test get_artist_songs function"""
        mock_artist_songs.return_value = {
            "songs": [{"title": "Hello"}, {"title": "Someone Like You"}]
        }
        songs = get_artist_songs(12345)
        self.assertEqual(len(songs), 2)
        self.assertEqual(songs[0]["title"], "Hello")

    @patch("main_tasks.lyricsgenius.Genius.artist_songs")
    def test_get_artist_songs_no_songs(self, mock_artist_songs):
        """test get_artist_songs function"""
        mock_artist_songs.return_value = {"songs": []}
        songs = get_artist_songs(12345)
        self.assertEqual(len(songs), 0)


if __name__ == "__main__":
    unittest.main()
