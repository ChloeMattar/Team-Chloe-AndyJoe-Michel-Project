def validate_genre_id(genre_id):
    if genre_id is None:
        return False
    elif not genre_id.isdigit():
        return False
    elif int(genre_id) <= 0: 
        return False
    else:
        return True

def validate_mood(mood):
    if mood in ["happy", "emotional", "romantic", "scary", "adventurous", "mind_bending"]:
        return True
    else: 
        return False 

def validate_person_name(name):
    if name is None:
        return False

    name = name.strip()

    if name == "":
        return False

    for char in name:
        if not (char.isalpha() or char in [" ", "-", "'", "’"]):
            return False

    return True
    
def validate_movie_id(movie_id):
    if movie_id is None:
        return False
    elif not movie_id.isdigit():
        return False
    elif int(movie_id) <= 0: 
        return False
    else:
        return True

def validate_page (page): 
    if page is None:
        return False
    elif not page.isdigit():
        return False
    elif int(page) <= 0: 
        return False
    else:
        return True


