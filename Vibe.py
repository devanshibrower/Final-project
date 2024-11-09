from dotenv import load_dotenv, find_dotenv
import os
from flask import Flask, render_template, redirect, request, session, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter
import time

# Load environment variables
load_dotenv(find_dotenv())

# Environment variables
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Set up Spotipy authentication
scope = "playlist-read-private"

# Add a function to create OAuth instance per user
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=scope,
        cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(session)
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
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

#callback function - called when user successfully logs in to grant access
@app.route('/callback')
def callback():
    try:
        sp_oauth = create_spotify_oauth()
        code = request.args.get('code')
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        session['token_info'] = token_info
        return redirect('/')
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        return redirect('/login')

#get artist information from playlist, genre is based on first artist
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

#check token from session
def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        return None
    
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        try:
            sp_oauth = create_spotify_oauth()
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
        except:
            return None
    
    return token_info

@app.route('/refresh-token')
def refresh_token():
    session_token = session.get('session_token', None)
    if not session_token:
        return redirect('/login')
        
    if is_token_expired(session_token):
        new_token = sp_oauth.refresh_access_token(session_token['refresh_token'])
        session['session_token'] = new_token
    return redirect('/')

def get_genre_counts(sp, playlist_id):
    tracks = sp.playlist_tracks(playlist_id)['items']
    artist_ids = []
    #loop through tracks to get artist ids
    for track in tracks:
        if 'track' in track:
            track_data = track['track']
            if 'artists' in track_data:
                artists = track_data['artists']
                if len(artists) > 0:
                    first_artist = artists[0]
                    if 'id' in first_artist:
                        artist_id = first_artist['id']
                        artist_ids.append(artist_id)    
                        artists = sp.artists(artist_ids)['artists']

    all_genres = []
    #loop through artists to get genres
    for artist in artists:
        if 'genres' in artist:
            genres = artist['genres']
            for genre in genres:
                all_genres.append(genre)

    genre_counts = Counter(all_genres)
    return dict(genre_counts.most_common(20))
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
