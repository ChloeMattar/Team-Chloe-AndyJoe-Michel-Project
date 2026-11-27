def validate_genre_id(genre_id):
    if genre_id is None:
        return False
    # Accept only standard numeric characters
    elif not genre_id.isascii() or not genre_id.isdigit():
        return False
    # Ensure the genre ID is a positive integer
    try:
        return int(genre_id) > 0
    except ValueError:
        return False

def validate_mood(mood):
    if mood in ["happy", "emotional", "romantic", "scary", "adventurous", "mind_bending"]:
        return True
    else: 
        return False 

def validate_person_name(name):
    if name is None:
        return False

    name = name.strip()

    # Reject empty or excessively long names
    if name == "" or len(name) > 100:
        return False

    # Ensure the name contains at least one letter
    if not any(char.isalpha() for char in name):
        return False

    # Allow letters, spaces, hyphens and apostrophes
    for char in name:
        if not (char.isalpha() or char in [" ", "-", "'", "’"]):
            return False

    return True
    
def validate_movie_id(movie_id):
    if movie_id is None:
        return False
    # Accept only standard numeric characters
    elif not movie_id.isascii() or not movie_id.isdigit():
        return False
    # Ensure the movie ID is a positive integer
    try:
        return int(movie_id) > 0
    except ValueError:
        return False

def validate_page(page):
    if page is None:
        return False
    # Accept only standard numeric characters
    elif not page.isascii() or not page.isdigit():
        return False
    # Ensure the page is within the allowed range
    try:
        return 1 <= int(page) <= 500
    except ValueError:
        return False


