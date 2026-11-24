import os
import requests  # you'll use this for the real API calls
from dotenv import load_dotenv 
load_dotenv() #loads variable of env into python environment
TMDB_TOKEN = os.environ.get("TMDB_TOKEN") #Reads the environment variables, not directly .env
BASE_URL = "https://api.themoviedb.org/3" 
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

TIMEOUT = 6  # seconds; give up instead of hanging if the API is slow

HEADERS = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json"
}

def tmdb_get(endpoint, params=None):
    """Send a GET request to TMDb and return its JSON data."""
    try:
        r = requests.get(BASE_URL + endpoint, 
    headers=HEADERS,
    params=params,
    timeout=TIMEOUT
    ) 
        if r.status_code != 200: 
            return None
        data = r.json()
    except requests.exceptions.JSONDecodeError as error:
        print("TMDb request failed:", error)
        return None
    except requests.exceptions.RequestException as error:
        print("TMDb request failed:", error)
        return None
    return data

def get_genre_map():
    genres_data = tmdb_get("/genre/movie/list")
    if genres_data is None:
        return {}
    genres = genres_data.get("genres", [])
    genre_map = {}
    for genre in genres:
        genre_id = genre.get("id")
        genre_name = genre.get("name")
        genre_map[genre_id] = genre_name
    return genre_map
    

def search(query):
    """Return a list of items matching the query."""
    data = tmdb_get("/search/movie", params={"query": query})

    if data is None:
        return[]
    genre_map = get_genre_map()
    return [{"id": x["id"], 
            "title": x.get("title", "Unknown Title"), 
            "image": IMAGE_BASE_URL + x["poster_path"] if x.get("poster_path") else None, 
            "release_date": x.get("release_date", ""), 
            "genres": [
                    genre_map.get(genre_id)
                    for genre_id in x.get("genre_ids", [])
                    if genre_id in genre_map],
            "vote_average": x.get("vote_average",None)
            }
             for x in data.get("results",[])]


def get_item(item_id):
    """Return one item by its id, or None if not found."""
    
    data = tmdb_get(
    f"/movie/{item_id}",
    params={"append_to_response": "credits,videos,similar"}
    )
    if data is None:
        return None
    return {
        "id" : data["id"],
        "title" : data["title"],
        "image": IMAGE_BASE_URL + data["poster_path"] if data.get("poster_path") else None,        
        "description" : data.get("overview",""),
        "genres" : data.get("genres",[]), 
        "runtime" : data.get("runtime"), 
        "vote_average" : data.get("vote_average", None),
        "cast": data.get("credits", {}).get("cast", []),
        "release_date": data.get("release_date", ""), 
        "trailers": [
        video for video in data.get("videos", {}).get("results", [])
        if video.get("type") == "Trailer"
        and video.get("site") == "YouTube"],
        "similar": [
            {"id": movie["id"], 
            "title": movie["title"], 
            "image": IMAGE_BASE_URL + movie["poster_path"] if movie.get("poster_path") else None,
            "release_date": movie.get("release_date"), 
            "vote_average": movie.get("vote_average")
            }
        
        for movie in data.get("similar", {}).get("results", [])
        ]
    }



       

