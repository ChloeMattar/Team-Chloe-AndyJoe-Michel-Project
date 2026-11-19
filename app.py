"""
<MatchIt> -- a Flask web app (team project starter).

Content comes from an external API (see api_client.py). The database stores user accounts, favorites, marathons, and marathon movies 
Authentication uses username, email, password,
and Flask sessions.

Run locally:   flask run --debug    ->   http://127.0.0.1:5000
"""
import os
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, abort)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Favorite, Marathon, MarathonMovie
import api_client

from validators import validate_signup, validate_login, validate_search

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")


def database_uri():
    """PostgreSQL on Render (DATABASE_URL), else a local SQLite file."""
    url = os.environ.get("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url
    return "sqlite:///" + os.path.abspath("app.db")


app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
with app.app_context():
    db.create_all()


@app.context_processor
def inject_globals():
    """Make the logged-in user (and their favorite ids) available in templates."""
    user = None
    favorite_ids = set()
    if "user_id" in session:
        user = db.session.get(User, session["user_id"])
        if user:
            favorite_ids = {int(f.movie_id)
                            for f in user.favorites
                            if f.movie_id.isascii() and f.movie_id.isdigit()} # convert to int for easier comparison in templates
    return {"current_user": user, "favorite_ids": favorite_ids}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ---------- content (from your API) --------------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    # Validate the search query
    error = validate_search(query)
    if error:
        flash(error)
        return render_template("results.html", items=[], query=query)
    
    # Search for movies using the TMDb API
    items = api_client.search(query)
    return render_template("results.html", items=items, query=query)


@app.route("/item/<item_id>")
def item(item_id):
    # Validate the movie ID
    if not item_id.isascii() or not item_id.isdigit() or int(item_id) <= 0:
        abort(404)
    data = api_client.get_item(item_id)
    if not data:
        abort(404)
    return render_template("detail.html", item=data)


# ===================================================================
# AUTHENTICATION  --  YOU BUILD THIS (sign-up, log-in, log-out, sessions)
# ===================================================================
# This is YOUR work. The routes below are stubs. Implement them using what
# you learned in the "Sessions & Login" slides. Tools already imported for
# you at the top: generate_password_hash, check_password_hash, session,
# and the validators validate_signup / validate_login.
#
# What each route should do:
#   signup (POST): validate the form; reject an email that already exists;
#                  hash the password; create the User; store session["user_id"];
#                  redirect home.
#   login  (POST): validate; find the user by email; check_password_hash;
#                  on success store session["user_id"]; else show an error.
#   logout        : session.clear(); redirect home.
# A worked version of favorites below shows how session["user_id"] is used.

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        errors, data = validate_signup(request.form) # Validate the submitted information
        if User.query.filter_by(username=data["username"]).first():
            errors["username"] = "Username already exists." # Check if username already exists
        if User.query.filter_by(email=data["email"]).first():
            errors["email"] = "Email already exists." # Check if email already exists
        if not errors:
            # Create the user
            user = User(
                username=data["username"],
                email=data["email"],
                password_hash=generate_password_hash(request.form.get("password","")))
            
            db.session.add(user)
            db.session.commit()
            # Store the user ID in the session
            session.clear()  # Clear any existing session data
            session["user_id"] = user.user_id
            flash("Account created successfully.")
            return redirect(url_for("home"))
        return render_template("signup.html", errors=errors, data=data)

    return render_template("signup.html", errors={}, data={})



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        errors, username = validate_login(request.form)
        # Find the user by username
        user = User.query.filter_by(username=username).first()
        # Check the username and password
        if not user or not check_password_hash(
            user.password_hash, request.form.get("password", "")
        ):
            errors["login"] = "Invalid username or password."
        if not errors:
            session.clear()
            session["user_id"] = user.user_id
            flash("Logged in successfully.")
            return redirect(url_for("home"))
        return render_template(
            "login.html",
            errors=errors,
            data={"username": username}
        )
    return render_template("login.html", errors={}, data={})

@app.route("/logout")
def logout():
    session.clear() # Clear the session to log the user out 
    return redirect(url_for("home"))


# ---------- favorites (login required) -----------------------------
@app.route("/favorites")
@login_required
def favorites():
    items = Favorite.query.filter_by(user_id=session["user_id"]).all()
    favorites = []
    for item in items:
        movie = api_client.get_item(item.movie_id) # get movie details from TMDb
        if movie: # check the API returned movie data instead of none
            favorites.append(movie)
    return render_template("favorites.html", favorites=favorites)


@app.route("/favorites/add", methods=["POST"])
@login_required
def favorites_add():
    item_id = request.form.get("item_id", "").strip()
    if not item_id.isascii() or not item_id.isdigit() or int(item_id) <= 0:
        flash("Invalid movie ID.")
        return redirect(url_for("favorites"))
    
    exists = Favorite.query.filter_by(
        user_id=session["user_id"], movie_id=item_id).first()
    if exists:
        flash("Already in your favorites.")
    else:
        db.session.add(Favorite(
         user_id=session["user_id"], movie_id=item_id,
        ))
        db.session.commit()
        flash("Saved to favorites.")
    return redirect(url_for("favorites"))


@app.route("/favorites/remove", methods=["POST"])
@login_required
def favorites_remove():
    item_id = request.form.get("item_id", "").strip()
    fav = Favorite.query.filter_by(
        user_id=session["user_id"], movie_id=item_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        flash("Removed from favorites.")
    return redirect(url_for("favorites"))

@app.route("/marathons")
@login_required
def marathons():
    items = Marathon.query.filter_by(user_id=session["user_id"]).all()
    return render_template("marathons.html",marathons=items)

@app.route("/marathons/create",methods=["POST"])
@login_required
def marathons_create():
    title = request.form.get("title", "").strip()
    if title == "":
        flash("Marathon title is required.")
        return redirect(url_for("marathons"))
    if len(title) > 255:
        flash("Marathon title is too large")
        return redirect(url_for("marathons"))
    marathon = Marathon(user_id=session["user_id"], title=title)
    
    db.session.add(marathon)
    db.session.commit()
    
    flash("Marathon created successfully.")
    return redirect(url_for("marathons"))

@app.route("/marathons/<int:marathon_id>")
@login_required
def marathon_details(marathon_id):
    # find the marathon belonging to the logged in user
    marathon = Marathon.query.filter_by(
        marathon_id=marathon_id,
        user_id=session["user_id"] #check which marathon and does it belong to the logged in user?
    ).first_or_404()
    
    # items contian all the movies inside a specific marathon
    items = MarathonMovie.query.filter_by(marathon_id=marathon_id).all()
    movies = []
    completed_ids = set()
    
    #for every movie inside this marathon, we get the fields and check if the movie is completed 
    for item in items:
        movie = api_client.get_item(item.movie_id)
        if movie:
            movies.append(movie)
            if item.is_completed:
                completed_ids.add(movie["id"])
    return render_template("marathon_details.html",marathon=marathon,movies=movies, completed_ids=completed_ids)

@app.route("/marathons/<int:marathon_id>/add", methods=["POST"])
@login_required
def marathon_add_movie(marathon_id):
    # find the marathon belonging to the logged in user
    marathon = Marathon.query.filter_by(
        marathon_id=marathon_id,
        user_id=session["user_id"] #check which marathon and does it belong to the logged in user?
    ).first_or_404()
    # Get the TMDb movie ID submitted by the HTML form
    movie_id = request.form.get("movie_id", "").strip()
    # Validate the movie ID received from the browser, even though TMDb normally provides valid IDs
    if not movie_id.isascii() or not movie_id.isdigit() or int(movie_id)<=0:
        flash("Invalid movie ID.")
        return redirect(url_for("marathon_details", marathon_id=marathon_id))
    #check if the movie is already in the marathon
    exists = MarathonMovie.query.filter_by(
        marathon_id=marathon_id,
        movie_id=movie_id
    ).first()
    if exists:
        flash("Movie already exists in this marathon.") 
    else:
        #add the movie to the marathon
        movie = MarathonMovie(
            marathon_id=marathon_id,
            movie_id=movie_id,
            is_completed=False
        )
        db.session.add(movie)
        db.session.commit()
        flash("Movie added successfully.")
    return redirect(url_for("marathon_details", marathon_id=marathon_id))

@app.route("/marathons/<int:marathon_id>/remove", methods=["POST"])
@login_required
def marathon_remove_movie(marathon_id):
    # find the marathon belonging to the logged in user
    marathon = Marathon.query.filter_by(
        marathon_id=marathon_id,
        user_id=session["user_id"] #check which marathon and does it belong to the logged in user?
    ).first_or_404()
    # Get the TMDb movie ID submitted by the HTML form
    movie_id = request.form.get("movie_id", "").strip()
    #check if the movie is already in the marathon
    movie = MarathonMovie.query.filter_by(
        marathon_id=marathon_id,
        movie_id=movie_id
    ).first()
    
    if movie:
        db.session.delete(movie)
        db.session.commit()
        flash("Movie removed from marathon.")
    else:
        flash("Movie not found in this marathon.")
    
    return redirect(url_for("marathon_details", marathon_id=marathon_id))
    
@app.route("/marathons/<int:marathon_id>/toggle", methods=["POST"])
@login_required
def marathon_toggle_movie(marathon_id):
    # find the marathon belonging to the logged in user
    marathon = Marathon.query.filter_by(
        marathon_id=marathon_id,
        user_id=session["user_id"] #check which marathon and does it belong to the logged in user?
    ).first_or_404()
    # Get the TMDb movie ID submitted by the HTML form
    movie_id = request.form.get("movie_id", "").strip()
    #check if the movie is already in the marathon
    movie = MarathonMovie.query.filter_by(
        marathon_id=marathon_id,
        movie_id=movie_id
    ).first()
    
    if movie:
        # swirch the completion status from false to true or true to false 
        movie.is_completed = not movie.is_completed 
        #save the updated completion status in the database
        db.session.commit()
        flash("Movie completion status updated.")
    else:
        flash("Movie not found in this marathon.")
        
    return redirect(url_for("marathon_details", marathon_id=marathon_id))

@app.route("/marathons/<int:marathon_id>/delete", methods=["POST"])
@login_required
def marathon_delete(marathon_id):
    # find the marathon belonging to the logged in user
    marathon = Marathon.query.filter_by(
        marathon_id=marathon_id,
        user_id=session["user_id"] #check which marathon and does it belong to the logged in user?
    ).first_or_404()
    
    #delete the marathon and its associated movie records 
    db.session.delete(marathon)
    db.session.commit()
    flash("Marathon deleted successfully.")
    return redirect(url_for("marathons"))

if __name__ == "__main__":
    app.run(debug=True)