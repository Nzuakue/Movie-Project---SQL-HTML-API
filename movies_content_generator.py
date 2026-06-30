import os
from dotenv import load_dotenv
import movies_storage.movies_storage_sql as storage

# Load .env file
load_dotenv()


def load_template_file():
    """Loads a template file"""
    with open(os.getenv("WEBSITE_TEMPLATE")) as f:
        return f.read()


def create_content():
    """
    Creates the content of the website

    :return str output: returns the content of the website
    """
    movies = storage.list_movies().fetchall()
    output = ""
    for movie in movies:
        print(movie)
        output += "<li>\n"
        output += "<div class=\"movie\">\n"
        output += f"<img class=\"movie-poster\" src=\"{movie.poster_image_url}\"/>\n"
        output += "<div class=\"movie-title\">"
        output += f"{movie.title}"
        output += "</div>\n"
        output += "<div class=\"movie-year\">"
        output += f"{movie.year}"
        output += "</div>\n"
        output += "</div>\n"
        output += "</li>\n"

    return output
