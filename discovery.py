from api_client import tmdb_get, get_genre_map, IMAGE_BASE_URL
import random

# Discover movies
def format_movie(movie_details, genre_map): # made for reusing it
    genre_names = []
    for genre_id in movie_details.get("genre_ids", []): # Convert genre ID to genre name
        genre_name = genre_map.get(genre_id)
        if genre_name:
            genre_names.append(genre_name)

    movie_dict = { # Movie fields details
        "id": movie_details.get("id"),
        "title": movie_details.get("title", "Unknown Title"),
        "image": IMAGE_BASE_URL + movie_details["poster_path"] if movie_details.get("poster_path") else None,
        "release_date": movie_details.get("release_date", ""),
        "vote_average": movie_details.get("vote_average", None),
        "genres": genre_names
    }

    return movie_dict

def discover_by_genre(genre_id): # Send a GET request to TMDb and return its movies by genre.
    params = {"with_genres": genre_id}
    data = tmdb_get("/discover/movie", params)
    if data is None:
        return []
    results = data.get("results", [])
    genre_map = get_genre_map()
    movies = []
    for movie_details in results:
        movies.append(format_movie(movie_details, genre_map)) # access reusable function
    return movies

mood_genres = {
    "happy": [35, 10751],
    "emotional": [18],
    "romantic": [10749],
    "scary": [27, 53],
    "adventurous": [28, 12],
    "mind-bending": [9648, 878]
}

def discover_by_mood(mood): # Send a request and return movies based on user's mood
    mood = mood.lower()
    genre_ids = mood_genres.get(mood)
    if genre_ids is None:
        return []
    genres = [] # add multiple genres based on 1 mood
    for genre_id in genre_ids:
        genres.extend(discover_by_genre(genre_id))
    return genres

def get_random_movie():
    data = tmdb_get("/discover/movie") # no parameter because the user will not enter anything
    if data is None:
        return None
    results = data.get("results", [])
    if not results:
        return None
    genre_map = get_genre_map()
    movie_details = random.choice(results)
    return format_movie(movie_details, genre_map)

def get_recommendations(movie_id):
    data = tmdb_get(f"/movie/{movie_id}/recommendations")
    if data is None:
        return []
    results = data.get("results", [])
    recommended_movie = []
    genre_map = get_genre_map()
    for movie_recommend in results:
        recommended_movie.append(format_movie(movie_recommend, genre_map)) # access reusable function
    return recommended_movie

# Search by actor - director
def search_person(name): # made for reusability in actor and director
    params = {"query": name}
    data = tmdb_get("/search/person", params) # requests all persons from tmdb and give the results as user entered
    if data is None:
        return []
    results = data.get("results", [])
    return results

def search_actor(name):
    results = search_person(name) # reuse of search_person instead of duplicating the code
    actors = []
    for actor in results:
        if actor.get("known_for_department") == "Acting": # gives only actors from persons
            actors.append(actor)
    return actors

def search_director(name):
    results = search_person(name)
    directors = []
    for director in results:
        if director.get("known_for_department") == "Directing": # gives only directors from persons
            directors.append(director)
    return directors
