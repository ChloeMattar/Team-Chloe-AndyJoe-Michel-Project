"""Server-side validation for sign-up and log-in."""
import re

EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def validate_signup(form):
    errors = {}
    username = form.get("username", "").strip()
    email = form.get("email", "").strip().lower()
    password = form.get("password", "")
    confirm = form.get("confirm", "")
    if username == "":
        errors["username"] = "Username is required."
    elif not re.fullmatch(r"[A-Za-z0-9_]{3,30}", username):
        errors["username"] = "Username must be 3-30 characters and contain only letters, numbers, and underscores."
    if email == "":
        errors["email"] = "Email is required."
    elif not EMAIL.fullmatch(email):
        errors["email"] = "Enter a valid email address."
    if password == "":
        errors["password"] = "Password is required."
    elif len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    if confirm == "":
        errors["confirm"] = "Please confirm your password."
    elif confirm != password:
        errors["confirm"] = "Passwords do not match."
    data = {"username":username, "email":email}
    return errors, data


def validate_login(form):
    errors = {}
    email = form.get("email", "").strip().lower()
    password = form.get("password", "")
    if email == "":
        errors["email"] = "Email is required."
    if password == "":
        errors["password"] = "Password is required."
    return errors, email
