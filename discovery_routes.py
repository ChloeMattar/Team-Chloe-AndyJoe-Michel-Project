from flask import Blueprint, request
from discovery_validators import validate_genre_id, validate_mood, validate_person_name, validate_movie_id,validate_page

discovery_bp = Blueprint("discovery", __name__)

@discovery_bp.route("/discover/genre")
def discover_genre():
    genre_id = request.args.get("genre_id")
    page = request.args.get("page", "1")
    if (not validate_genre_id(genre_id)):
        return f"Invalid Genre ID", 400
    elif (not validate_page(page)):
        return f"Invalid Page", 400
    else: 
        return f"Genre ID: {genre_id} Page: {page}"

@discovery_bp.route("/discover/mood")
def discover_mood():
    mood = request.args.get("mood")
    page = request.args.get("page", "1")
    if (not validate_mood(mood)):
        return f"Invalid Mood", 400
    elif (not validate_page(page)):
        return f"Invalid Page", 400
    else:
        return f"Mood: {mood} Page: {page}"

@discovery_bp.route("/search/actor")
def search_actor():
    name = request.args.get("name")
    page = request.args.get("page", "1")
    if (not validate_person_name(name)):
        return f"Invalid Name", 400
    elif (not validate_page(page)):
        return f"Invalid Page", 400
    else:
        return f"Name: {name} Page: {page}"

@discovery_bp.route("/search/director")
def search_director():
    name = request.args.get("name")
    page = request.args.get("page", "1")
    if (not validate_person_name(name)):
        return f"Invalid Name", 400
    elif (not validate_page(page)):
        return f"Invalid Page", 400
    else:
        return f"Name: {name} Page: {page}"


@discovery_bp.route("/random")
def random_movie (): 
    return f"Random movie route works!"

@discovery_bp.route("/recommendations/<movie_id>")
def get_movie_recommendations(movie_id):
    if (not validate_movie_id(movie_id)):
        return f"Invalid Movie ID", 400
    else:
        return f"Recommendations for movie ID: {movie_id}"

@discovery_bp.route("/discover")
def discover_page (): 
    return "Discover page works!"