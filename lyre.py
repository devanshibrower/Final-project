from dotenv import load_dotenv, find_dotenv
import os
from flask import Flask, render_template, redirect, request, session, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter
from collections import defaultdict
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
    print("Accessing login route")
    auth_url = sp_oauth.get_authorize_url()
    print(f"Generated auth URL: {auth_url}")
    return redirect(auth_url)

@app.route('/callback')
def callback():
    print("Accessing callback route")
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    print("Token info saved to session, redirecting to playlists")
    return redirect('/playlists')

@app.route('/playlists')
def playlists():
    # Your existing code to fetch playlists
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = sp.current_user_playlists()
    
    # For demonstration, let's use the first playlist to get genre counts
    if results['items']:
        first_playlist_id = results['items'][0]['id']
        genre_counts = get_genre_counts(sp, first_playlist_id)
    else:
        genre_counts = {}  # Empty dict if no playlists found
    
    return render_template('index.html', playlists=results['items'], genre_counts=genre_counts)

@app.route('/get_genre_counts/<playlist_id>')
def get_genre_counts_for_playlist(playlist_id):
    token_info = get_token()
    if not token_info:
        return jsonify({'error': 'Not authenticated'}), 401
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    genre_counts = get_genre_counts(sp, playlist_id)
    print(f"Genre counts for playlist {playlist_id}: {genre_counts}")  # Add this line
    return jsonify(genre_counts)

def calculate_genre_counts(songs):
    genre_counts = {}
    for song in songs.values():
        genre = song.get('genre', 'Unknown')
        if genre in genre_counts:
            genre_counts[genre] += 1
        else:
            genre_counts[genre] = 1
    return genre_counts

def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        return None
    
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info
    
    return token_info

def get_genre_counts(sp, playlist_id):
    # Get tracks from the playlist
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    
    # Extract artist IDs
    artist_ids = [track['track']['artists'][0]['id'] for track in tracks if track['track']]
    
    # Get artist details including genres
    artists = sp.artists(artist_ids)['artists']
    
    # Collect all genres
    all_genres = [genre for artist in artists for genre in artist['genres']]
    
    # Count genres
    genre_counts = Counter(all_genres)
    
    # Limit to top 20 genres
    top_genres = dict(genre_counts.most_common(20))
    
    print(f"Top genres for playlist {playlist_id}: {top_genres}")  # Add this line
    return top_genres

if __name__ == '__main__':
    app.run(debug=True, port=5001)
