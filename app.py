from flask import Flask, render_template, request
import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Load Spotify API credentials from environment variables
CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load your music data and similarity matrix
music = pickle.load(open('./model/df.pkl', 'rb'))
similarity = pickle.load(open('./model/similarity.pkl', 'rb'))

def get_song_info(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track", market="US")
    print(results)
    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        song_url = track["external_urls"]["spotify"]
        album_cover_url = track["album"]["images"][0]["url"]
        return song_url, album_cover_url
    else:
        return "/", "https://i.postimg.cc/0QNxYz4V/social.png"
    
@app.route('/', methods=['GET', 'POST'])
def music_recommendation():
    if request.method == 'POST':
        selected_song = request.form.get('song')
        index = music[music['song'] == selected_song].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_music_names = []
        recommended_music_posters = []
        recommended_music_urls = []
        for i in distances[1:6]:
            artist = music.iloc[i[0]].artist
            song_url, album_cover_url = get_song_info(music.iloc[i[0]].song, artist)
            recommended_music_urls.append(song_url)
            recommended_music_posters.append(album_cover_url)
            recommended_music_names.append(music.iloc[i[0]].song)

        return render_template('index.html', music_list=music['song'].values, recommended_music_names=recommended_music_names, recommended_music_posters=recommended_music_posters, recommended_music_urls=recommended_music_urls)

    return render_template('index.html', music_list=music['song'].values)

if __name__ == "__main__":
    app.run()