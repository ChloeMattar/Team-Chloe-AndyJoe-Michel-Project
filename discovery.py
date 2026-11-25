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

def discover_by_genre(genre_id,page=1): # Send a GET request to TMDb and return its movies by genre.
    params = {"with_genres": genre_id, "page": page}
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
    "mind_bending": [9648, 878]
}

def discover_by_mood(mood, page=1):
    mood = mood.lower()
    genre_ids = mood_genres.get(mood)
    if genre_ids is None:
        return []
    genres = []
    seen_ids = set()
    for genre_id in genre_ids:
        movies = discover_by_genre(genre_id, page)
        for movie in movies:
            if movie["id"] not in seen_ids:
                genres.append(movie)
                seen_ids.add(movie["id"])
    return genres

def get_random_movie():
    data = tmdb_get("/discover/movie")
    if data is None:
        return None
    total_pages = data.get("total_pages", 0)
    if total_pages == 0:
        return None
    random_page = random.randint(1, min(total_pages, 500))
    data = tmdb_get("/discover/movie", {"page": random_page})
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
    results = search_person(name)
    movies = []
    seen_ids = set()
    genre_map = get_genre_map()
    for actor in results:
        if actor.get("known_for_department") == "Acting":
            actor_id = actor.get("id")
            if actor_id is None:
                continue
            data = tmdb_get(f"/person/{actor_id}/movie_credits", None)
            if data is None:
                continue
            for movie in data.get("cast", []):
                movie_id = movie.get("id")
                if movie_id is not None and movie_id not in seen_ids:
                    movies.append(format_movie(movie, genre_map))
                    seen_ids.add(movie_id)
    return movies

def search_director(name):
    results = search_person(name)
    movies = []
    seen_ids = set()
    genre_map = get_genre_map()
    for director in results:
        if director.get("known_for_department") == "Directing":
            director_id = director.get("id")
            if director_id is None:
                continue
            data = tmdb_get(f"/person/{director_id}/movie_credits", None)
            if data is None:
                continue
            for movie in data.get("crew", []):
                if movie.get("job") == "Director":
                    movie_id = movie.get("id")
                    if movie_id is not None and movie_id not in seen_ids:
                        movies.append(format_movie(movie, genre_map))
                        seen_ids.add(movie_id)
    return movies



