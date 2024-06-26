# Song_Sentiment_Analysis

![style check workflow](https://github.com/kuruefebeste/Song_Sentiment_Analysis/actions/workflows/code_check.yaml/badge.svg?event=push)

![unit test workflow](https://github.com/kuruefebeste/Song_Sentiment_Analysis/actions/workflows/unit_test.yaml/badge.svg?event=push)

## Project Description:

Song Sentiment_Analyzer is a Python project that performs sentiment analysis on the titles of the most popular twenty songs by a given artist. It uses the Genius API to access song titles and the Text-Processing API to analyze the sentiment of these titles. The results are stored in a SQLite database and printed out for further analysis.

## Setup

1. Clone the repository from this link: https://github.com/kuruefebeste/Song_Sentiment_Analysis.git

2. Make sure you have these installed:
* requests
* json
* sqlalchemy
* pandas
* os
* lyricsgenius

3. Create your Genius API account and set up an environment variable for the Genius API Client Access Token:

```export CLIENT_ACCESS_TOKEN='your_genius_api_token'``` 

## Usage

1. Make sure you have saved your environment variables by running this command:
```source ~/.bashrc```

2. Run:
```python3 main_tasks.py```

3. Enter the names of the artists when prompted. For example:

- Enter the name of an artist: Ed Sheeran
- Enter the name of an artist: Britney Spears
- Enter the name of an artist: Justin Timberlake

4. The script will fetch the top 20 popular songs for each artist, perform sentiment analysis on the song titles, and display the results.



