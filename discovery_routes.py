from flask import Blueprint, request,render_template, redirect, url_for
from discovery_validators import validate_genre_id, validate_mood, validate_person_name, validate_movie_id,validate_page
from api_client import get_genre_map
from discovery import discover_by_genre, discover_by_mood, search_actor as api_search_actor, search_director as api_search_director, get_random_movie, get_recommendations
import api_client
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
        # Retrieve movies and pagination information
        movies, total_pages = discover_by_genre(genre_id, int(page), include_pagination=True)
        error = None
        # Handle TMDb API request failure
        if total_pages is None:
            error = "Unable to retrieve movies. Please try again later."
        # Pass the results, pagination and error message to the template
        return render_template("discovery_results.html", movies=movies, page=int(page), genre_id=genre_id, total_pages=total_pages, error=error)

@discovery_bp.route("/discover/mood")
def discover_mood():
    mood = request.args.get("mood")
    page = request.args.get("page", "1")
    if (not validate_mood(mood)):
        return f"Invalid Mood", 400
    elif (not validate_page(page)):
        return f"Invalid Page", 400
    else:
        # Retrieve mood movies and pagination information
        movies, total_pages = discover_by_mood(mood, int(page), include_pagination=True)
        error = None
        # Handle complete or partial API request failures
        if total_pages is None:
            if movies:
                error = "Some movies could not be retrieved. Please try again later."
            else:
                error = "Unable to retrieve movies. Please try again later."
        # Pass the results, pagination and error message to the template
        return render_template("discovery_results.html", movies=movies, page=int(page), mood=mood, total_pages=total_pages, error=error)

@discovery_bp.route("/search/actor")
def search_actor():
    name = request.args.get("name")
    page = request.args.get("page", "1")
    if (not validate_person_name(name)):
        return f"Invalid Name", 400
    elif (not validate_page(page)):
        return f"Invalid Page", 400
    else:
        # Retrieve actor movies and pagination information
        movies, total_pages = api_search_actor(name, int(page), include_pagination=True)
        error = None
        # Handle complete or partial API request failures
        if total_pages is None:
            if movies:
                error = "Some movies could not be retrieved. Please try again later."
            else:
                error = "Unable to retrieve movies. Please try again later."
        # Pass the results, pagination and error message to the template
        return render_template("discovery_results.html", movies=movies, page=int(page), total_pages=total_pages, search_type="actor", query=name, error=error)

@discovery_bp.route("/search/director")
def search_director():
    name = request.args.get("name")
    page = request.args.get("page", "1")
    if (not validate_person_name(name)):
        return f"Invalid Name", 400
    elif (not validate_page(page)):
        return f"Invalid Page", 400
    else:
        # Retrieve director movies and pagination information
        movies, total_pages = api_search_director(name, int(page), include_pagination=True)
        error = None
        # Handle complete or partial API request failures
        if total_pages is None:
            if movies:
                error = "Some movies could not be retrieved. Please try again later."
            else:
                error = "Unable to retrieve movies. Please try again later."
        # Pass the results, pagination and error message to the template
        return render_template("discovery_results.html", movies=movies, page=int(page), total_pages=total_pages, search_type="director", query=name, error=error)


@discovery_bp.route("/random")
def random_movie (): 
    movie = get_random_movie ()
    if movie is None:
        return f"No movie was selected", 503
    else:
        return redirect(url_for("item", item_id=movie["id"], from_random=1))

@discovery_bp.route("/recommendations/<movie_id>")
def get_movie_recommendations(movie_id):
    if not validate_movie_id(movie_id):
        return "Invalid Movie ID", 400
    else:
        movies = get_recommendations(movie_id)
        return render_template("discovery_results.html", movies=movies, search_type="recommendations")

@discovery_bp.route("/recommendations")
def recommendations_page():
    return render_template("recommendations.html")

@discovery_bp.route("/discover")
def discover_page (): 
    genres = get_genre_map()
    return render_template("discover.html", genres=genres)

@discovery_bp.route("/pick-movie")
def pick_movie():
    return render_template("pick_movie.html")

@discovery_bp.route("/recommendations/select")
def select_recommendation_movie():
    query = request.args.get("q", "").strip()
    movies = []
    if query:
        movies = api_client.search(query)
    return render_template("select_movie.html", movies=movies, query=query)