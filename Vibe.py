from dotenv import load_dotenv, find_dotenv
import os
from flask import Flask, render_template, redirect, request, session, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter
import time

# Load environment variables
load_dotenv(find_dotenv())

# Now you can access your environment variables
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Set up Spotipy authentication
scope = "playlist-read-private"
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope
)


@app.route('/')
@app.route('/playlists')
def index():
    token_info = get_token()
    if not token_info:
        return redirect('/login')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_playlists()
    
    genre_counts = {}
    if results['items']:
        first_playlist_id = results['items'][0]['id']
        genre_counts = get_genre_counts(sp, first_playlist_id)
    
    print("Initial genre counts:", genre_counts)  # Add this line for debugging
    return render_template('index.html', playlists=results['items'], genre_counts=genre_counts)

@app.route('/login')
def login():
    return redirect(sp_oauth.get_authorize_url())

@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args.get('code'))
    session['token_info'] = token_info
    return redirect('/')  # Changed from '/playlists' to '/'

@app.route('/get_genre_counts/<playlist_id>')
def get_genre_counts_route(playlist_id):
    token_info = get_token()
    if not token_info:
        return jsonify({"error": "Not authenticated"}), 401
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    try:
        genre_counts = get_genre_counts(sp, playlist_id)
        return jsonify(genre_counts)
    except Exception as e:
        print(f"Error fetching genre counts: {str(e)}")
        return jsonify({"error": "Failed to fetch genre counts"}), 500


def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        return None
    
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
        except:
            return None
    
    return token_info

def get_genre_counts(sp, playlist_id):
    tracks = sp.playlist_tracks(playlist_id)['items']
    artist_ids = [track['track']['artists'][0]['id'] for track in tracks if track['track']]
    artists = sp.artists(artist_ids)['artists']
    all_genres = [genre for artist in artists for genre in artist['genres']]
    genre_counts = Counter(all_genres)
    return dict(genre_counts.most_common(20))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
