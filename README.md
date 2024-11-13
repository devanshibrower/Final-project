# CS50 Final Project: VIBE

# VIBE
#### Video Demo:  <URL HERE>
#### Description: Vibe is a fun web application that provides a visual representation of the music genres within a playlist. Inspired by data visualization tools like the "Grand Perspective" app for visualizing memory usage, Vibe allows users to view the genre composition of their playlists in a visually appealing and interactive manner using a treemap. Each rectangle within the treemap represents a music genre, with its size proportional to the number of songs of that genre in the selected playlist.

The goal of Vibe is to offer an insightful, engaging way for users to explore their music taste by viewing genre distributions interactively. By connecting with the Spotify API, users can visualize their own playlists in real-time.

Features:
- Users can login into their Spotify account and visualize their own playlists
- Treemap visualization of genre distribution in selected playlist in real-time


Files included:
- Templates/index.html: The main HTML template for the application
- Static/script.js: The main JavaScript file for the application, to separate the code for handling custom gradients of the treemap visualization, utilizing D3.js to generate the dynamic and data-driven SVG elements.
- Static/styles.css: The main CSS file for the application
- vibe.py: The main Flask application that handles routing, authentication, and interaction with Spotify's API.
- .env: This file stores sensitive information such as Spotify API credentials (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI). It is not included in the repository for security reasons.

Design Choices:
**Treemap for Genre Visualization**: A treemap was chosen to visually represent the hierarchical distribution of music genres due to its ability to show both the proportion and the relationship between different genres effectively. This allows users to quickly grasp their listening habits at a glance. Also for fun, inspired by the "Grand Perspective" app for visualizing memory usage.  

**D3.js for Interactivity**: D3.js was used to create the treemap visualization because of its flexibility in rendering dynamic and interactive data visualizations.Initially had challenges with visualizing large number of genres, which was solved by limiting to top 20 genres. 

**Spotify API Integration**: To make the experience personal, the application integrates with Spotify's API, allowing users to visualize their own playlists rather than a generic dataset. This decision was made to create a more engaging experience by using real data from users' listening history.

**Gradient Styling for Genres**: Custom gradients were applied to each genre to make the treemap aesthetically pleasing and match my figma designs. 

Setup instructions:
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install the following:
    - Flask: web framework
    - Spotipy: Spotify API wrapper
    - Python-dotenv: to load environment variables from .env file
4. Create a Spotify Developer account and register your application:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Note: The app is in Development Mode, which means:
     - Only users listed in the Dashboard can access the app
     - Maximum of 25 users can be added
     - You'll need to add the email associated with any Spotify account that wants to test the app
6. Add test users:
   - In your Spotify Developer Dashboard, select your app
   - Go to 'Users and Access'
   - Add the Spotify email addresses of any testers
7. Create a .env file with your Spotify credentials:
   ```
   SPOTIPY_CLIENT_ID=your_client_id
   SPOTIPY_CLIENT_SECRET=your_client_secret
   SPOTIPY_REDIRECT_URI=http://localhost:5001/callback
   ```
8. Run the application: `python vibe.py`

Note: Due to Spotify's Development Mode restrictions, only users whose email addresses have been added to the Dashboard will be able to log in and use the application. If you need to test the application, please contact the developer to have your Spotify email added to the allowed users list.

Conclusion
Vibe is a fun tool for anyone interested in exploring their music tastes in a visual format. By connecting directly with Spotify, Vibe turns a user's playlist data into a beautiful and informative visual story. 

Through this project, I gained a deeper understanding of integrating APIs, using data visualization libraries like D3.js and refining front end development skills to match my figma designs.
