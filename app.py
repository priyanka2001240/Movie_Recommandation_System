import streamlit as st
import pandas as pd
import requests
import urllib.parse

# Set the page configuration
st.set_page_config(page_title="MovieNest", layout="wide")

# Function to display logo and title (shown on every page)
def display_logo_and_title():
    col1, col2 = st.columns([1, 2])  # Adjust ratios as needed

    # Place the logo in the first column
    with col1:
        st.image("logo_movie.png", width=200)  # Adjust logo siz

    # Place the movie title in the second column
    with col2:
        st.markdown(
            """
            <style>
            body {
                font-family: 'Arial', sans-serif;  
            }
            </style>
           <h1 style=" font-size: 120px; font-family:Candara">MovieNest</h1>
           <h4 style= "margin-left: -250px; "><i>Explore a personalized movie journey, where every recommendation brings you closer to the stories you’ll love</i></h4>
            """,
            unsafe_allow_html=True
        )

# Display the logo and title on all pages
display_logo_and_title()

# Define the 'Home' page layout with an icon (aligned horizontally)
def display_home():
    col1, col2 = st.columns([0.08, 1])

    # Display the home icon in the first column
    with col1:
        st.image("home1.png", width=70)  # Adjust the size of the home icon
       
    # Display "Home" text in the second column
    with col2:
        st.markdown(
            """
            <h1 style="margin-left: -40px; font-size: 50px; font-family: Math;">Home</h1>
<p style="font-size: 25px; font-family: serif; margin-left: -40px; text-align: justify;">
    <i>Welcome to our Movie Recommender System – a personalized cinematic guide designed to make discovering your next favorite movie effortless and enjoyable. In a world filled with countless films, finding the perfect one can feel overwhelming. Our system is here to change that. With advanced algorithms and thoughtful recommendations, we bring you tailored suggestions based on your unique taste, ensuring each recommendation aligns with your preferences and mood. From hidden gems to celebrated classics, our recommender curates a selection that matches your interests. Whether you’re looking for genre-specific films, movies from your favorite actors or directors, or highly-rated blockbusters, our intuitive platform makes exploration simple and enjoyable. Join us and dive into a world where every movie recommendation is a step closer to a memorable viewing experience.</i>
</p>
            """,
            unsafe_allow_html=True
        )

# Load the dataset
try:
    df = pd.read_csv('movies_data_with_imdb_links.csv')
    
    # Fill missing values
    df['Genre'] = df['Genre'].fillna('')
    df['Year'] = df['Year'].fillna('')

    # Convert Year to numeric
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

    # Split the Genre column by commas and expand so that each genre gets its own row
    df = df.assign(Genre=df['Genre'].str.split(',')).explode('Genre')

    # Strip any leading or trailing whitespace in genres
    df['Genre'] = df['Genre'].str.strip()

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Define OMDb API key
OMDB_API_KEY = '2b46b776'  # Replace with your actual OMDb API key

# Fetch movie details from OMDb API
@st.cache_data
def get_movie_details(title, year=None):
    try:
        encoded_title = urllib.parse.quote(title)
        url = f"http://www.omdbapi.com/?t={encoded_title}&y={year}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data.get('Response') == 'True':
            poster_url = data.get('Poster')
            imdb_rating = data.get('imdbRating') if data.get('imdbRating') != 'N/A' else "N/A"
            plot = data.get('Plot') if data.get('Plot') != 'N/A' else "Plot not available."
            return poster_url, imdb_rating, plot
        else:
            return None, None, None
    except Exception as e:
        st.error(f"Error fetching details for {title} ({year}): {e}")
        return None, None, None

# Display movie details
def display_movie_details(movie_title, movie_year=None):
    poster_url, imdb_rating, plot = get_movie_details(movie_title, movie_year)
    if poster_url is None:
        return

    imdb_link_row = df[(df['Name'] == movie_title) & (df['Year'] == movie_year)]['IMDb_Link']
    imdb_link = imdb_link_row.values[0] if not imdb_link_row.empty else "https://via.placeholder.com/150"
    movie_year = int(movie_year) if movie_year else "N/A"

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <a href="{imdb_link}" target="_blank">
            <img src="{poster_url}" width="150" style="margin-bottom: 20px; border-radius: 10px;">
        </a>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        Title: [{movie_title}]({imdb_link})  
        Year: {movie_year}  
        IMDb Rating: {imdb_rating}  
        Plot: {plot}
        """)

# Navigation bar at the top
st.markdown("""
    <style>
    .nav-bar {
        background-color: #f0f0f0;
        padding: 10px;
        margin-bottom: 20px;
        border-radius: 30px;
        font-family: 'Georgia', sans-serif;
        text-align: center;
        margin-top: 40px;     
    }
    .nav-bar a {
        color: #008CBA;
        margin: 0 10px;
        font-weight: bold;
        text-decoration: none;
        padding: 10px;
        border-radius: 5px;
        background-color: #f1f1f1;
    }
    .nav-bar a:hover {
        background-color: #ddd;
        color: #005f6b;
    }
    </style>
    <div class="nav-bar">
        <a href="?page=home">Home</a>
        <a href="?page=genre">Genre</a>
        <a href="?page=actor">Actor</a>
        <a href="?page=director">Director</a>
        <a href="?page=rate">Rate a Movie</a>
    </div>
    """, unsafe_allow_html=True)

# Access query parameters
params = st.query_params  # st.query_params is now an attribute, not a function
page = params.get('page', 'home')

# Navigation pages
if page == 'home':
    display_home()  # Display the 'Home' page with an icon and text

elif page == "genre":
    # st.header("🎭 Movies by Genre")
    st.markdown(
        "<h1 style='text-align: cleft; color: #4ffff; font-family: math, monospace; font-size: 2.5em;'>🎭 Movies by Genre</h1>",
        unsafe_allow_html=True
    )
    genre_options = sorted(df['Genre'].unique())  # Sort genres alphabetically
    
    # Using selectbox to directly display movies based on genre
    selected_genre = st.selectbox('Select a genre:', genre_options)

    # Add a "Find Movies" button
    if st.button("Find Movies"):
        if selected_genre:
            genre_movies = df[df['Genre'].str.contains(selected_genre, case=False, na=False)][['Name', 'Year']]

            if not genre_movies.empty:
                displayed_movies = set()  # Track displayed movies
               # st.write(f"### {len(genre_movies)} Movies found in {selected_genre} genre:")
                for idx, row in genre_movies.iterrows():
                    movie_title = row['Name']
                    movie_year = row['Year']
                    
                    if movie_title not in displayed_movies:  # Display only once
                        display_movie_details(movie_title, movie_year)
                        displayed_movies.add(movie_title)  # Add to displayed set
            else:
                st.warning("No movies found for the selected genre.")
        else:
            st.warning("Please select a genre.")

elif page == "actor":
    # st.header("🎬 Movies by Actor")
    st.markdown(
        "<h1 style='text-align: left; color: #ffff; font-family:math, monospace; font-size: 2.5em;'>🎬 Movies by Actor</h1>",
        unsafe_allow_html=True
    )
    actor_options = sorted(pd.concat([df['Actor 1'], df['Actor 2'], df['Actor 3']]).unique())  # Sort actors alphabetically
    actor_name = st.selectbox("Select an actor:", actor_options)

    # Add a "Find Movies" button
    if st.button("Find Movies"):
        if actor_name:
            actor_movies = df[(df['Actor 1'] == actor_name) | (df['Actor 2'] == actor_name) | (df['Actor 3'] == actor_name)][['Name', 'Year']]
            
            if not actor_movies.empty:
                displayed_movies = set()  # Track displayed movies
                #st.write(f"### {len(actor_movies)} Movies featuring {actor_name}:")
                for idx, row in actor_movies.iterrows():
                    movie_title = row['Name']
                    movie_year = row['Year']
                    
                    if movie_title not in displayed_movies:  # Display only once
                        display_movie_details(movie_title, movie_year)
                        displayed_movies.add(movie_title)  # Add to displayed set
            else:
                st.warning("No movies found for the selected actor.")
        else:
            st.warning("Please select an actor.")

elif page == "director":
    # st.header("🎥 Movies by Director")
    st.markdown(
        "<h1 style='text-align: left; color: #ffff; font-family:math, monospace; font-size: 2.5em;'>🎥 Movies by Director</h1>",
        unsafe_allow_html=True
    )
    director_options = sorted(df['Director'].unique())  # Sort directors alphabetically
    director_name = st.selectbox("Select a director:", director_options)

    # Add a "Find Movies" button
    if st.button("Find Movies"):
        if director_name:
            director_movies = df[df['Director'].str.contains(director_name, case=False)][['Name', 'Year']]
            
            if not director_movies.empty:
                displayed_movies = set()  # Track displayed movies
                #st.write(f"### {len(director_movies)} Movies directed by {director_name}:")
                for idx, row in director_movies.iterrows():
                    movie_title = row['Name']
                    movie_year = row['Year']
                    
                    if movie_title not in displayed_movies:  # Display only once
                        display_movie_details(movie_title, movie_year)
                        displayed_movies.add(movie_title)  # Add to displayed set
            else:
                st.warning("No movies found for the selected director.")
        else:
            st.warning("Please select a director.")

elif page == "rate":
    # st.header("🌟 Rate a Movie")
    st.markdown(
        "<h1 style='text-align: left; color: #ffff; font-family: math, monospace; font-size: 2.5em;'> ⭐Rate a Movie</h1>",
        unsafe_allow_html=True
    )
    rating_options = sorted(df['Name'].unique())  # Sort movie titles alphabetically
    selected_movie = st.selectbox("Select a movie to rate:", rating_options)

    if selected_movie:
        rating = st.slider("Rate the movie (1 to 5):", min_value=1, max_value=5)

        if st.button("Submit Rating"):
            st.success(f"Thank you for rating '{selected_movie}' with {rating} stars!")

# Add footer
st.markdown("""
    <style>
    footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #202025;
        color: #f0f0f0;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        }
    </style>
    <footer>
    <p>© 2024 MovieNest | All rights reserved.</p>
    </footer>
""", unsafe_allow_html=True)