import os
from sqlalchemy import create_engine, text
import requests
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from main import get_active_user

# Load the .env file from current directory
load_dotenv()

DB_URL = os.getenv("DB_URL")
API_KEY = os.getenv("API_KEY")
MOVIES_API_URL = "http://www.omdbapi.com/"

# Create the engine
engine = create_engine(DB_URL, echo=False)

create_tables_stmt = """
    CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT COLLATE NOCASE UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    rating REAL NOT NULL,
    poster_image_url TEXT,
    user_name TEXT NOT NULL
);
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT COLLATE NOCASE UNIQUE NOT NULL
);
"""

# Create movies tables if thy do not exist.
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT COLLATE NOCASE UNIQUE NOT NULL,
        year INTEGER NOT NULL,
        rating REAL NOT NULL,
        poster_image_url TEXT,
        user_id INTEGER NOT NULL
        )
    """))
    connection.commit()

# Create users table if thy do not exist.
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT COLLATE NOCASE UNIQUE NOT NULL
        )
    """))
    connection.commit()


# CRUD functions for movies
def fetch_data(title):
    """
    Fetches movie data from API.

    :param str title: movie title
    :return dict: movie data
    """
    params = {"t": title, "apikey": API_KEY}
    try:
        movie = requests.get(MOVIES_API_URL, params).json()
        if "Error" in movie and "movie not found".lower() in movie["Error"].lower():
            raise Exception(f"Movie \"{title}\" not found!")
    except Exception as e:
        error_msg = str(e)
        if "NameResolutionError" in error_msg:
            print("Please check your internet connection.")
        else:
            print(f"Error: {error_msg}")
    else:
        return {movie["Title"]: {"year": movie["Year"], "rating": float(movie["imdbRating"]),
                                 "poster_image_url": movie["Poster"]}}
    finally:
        requests.Session().close()


def add_movie(title):
    """
    Add a new movie to the database fetching it from API.

    :param str title: movie to be added
    """
    with engine.connect() as connection:
        try:
            movie = fetch_data(title)
            movie_title = list(movie.keys())[0]
            year = movie.get(movie_title).get("year")
            rating = movie.get(movie_title).get("rating")
            poster_image_url = movie.get(movie_title).get("poster_image_url")
            connection.execute(text(
                "INSERT INTO movies (title, year, rating, poster_image_url, user_id) VALUES (:movie_title, :year, :rating, :poster_image_url, :user_name)"),
                {"movie_title": movie_title, "year": year, "rating": rating, "poster_image_url": poster_image_url,
                 "user_name": get_active_user()})
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except IntegrityError as e:
            error_msg = str(e).lower()
            if "unique" in error_msg:
                print(f"Movie \"{title}\" already exist!")
        except Exception as e:
            print(f"Error: {e}")


def list_movies():
    """
    Retrieve all movies from the database.
    """
    with engine.connect() as connection:
        return connection.execute(
            text("SELECT title, year, rating, poster_image_url FROM movies WHERE user_name = :user_name"),
            {"user_name": get_active_user()})


def update_movie(title, rate):
    """
    Update a movies rating in the database.

    :param str title: movie to be updated
    :param float rate: movie rate
    """
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text("UPDATE movies SET rating = :new_rate WHERE title = :title and user_id = :user_name"),
                {"new_rate": rate, "title": title, "user_name": get_active_user()})
            connection.commit()
            if result.rowcount == 0:
                print(f"Movie \"{title}\" does not exist.")
            elif result.rowcount > 0:
                print(f"Movie \"{title}\" updated successfully.")
        except Exception as e:
            print(f"Error: {e}")


def delete_movie(title):
    """
    Delete a movie from the database.

    :param str title: movie to be deleted
    """
    with engine.connect() as connection:
        try:
            result = connection.execute(text("DELETE FROM movies WHERE title = :title and user_name = :user_name"),
                                        {"title": title, "user_name": get_active_user()})
            connection.commit()
            if result.rowcount == 0:
                print(f"Movie '{title}' does not exist.")
            elif result.rowcount > 0:
                print(f"Movie '{title}' deleted successfully.")
        except Exception as e:
            print(f"Error: {e}")


# CRUD functions for users
def add_user(name):
    """
    Add a new user to the database.

    :param str name: username
    """
    with engine.connect() as connection:
        try:
            connection.execute(text(
                "INSERT INTO users (name) VALUES (:name)"), {"name": name})
            connection.commit()
            print(f"User \"{name}\" added successfully.")
        except IntegrityError as e:
            error_msg = str(e).lower()
            if "unique" in error_msg:
                print(f"User \"{name}\" already exist!")
        except Exception as e:
            print(f"Error: {e}")


def list_users():
    """
    Retrieve all users from the database.
    """
    with engine.connect() as connection:
        return connection.execute(text("SELECT name FROM users"))


def update_user(old_name, new_name):
    """
    Update an username in the database.

    :param str old_name: old username
    :param str new_name: new username
    """
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text("UPDATE movies SET name = :new_name WHERE name = :old_name"),
                {"new_name": new_name, "old_name": old_name})
            connection.commit()
            if result.rowcount == 0:
                print(f"User \"{old_name}\" does not exist.")
            elif result.rowcount > 0:
                print(f"User \"{old_name}\" updated successfully.")
        except Exception as e:
            print(f"Error: {e}")


def delete_user(name):
    """
    Delete an user from the database.

    :param str name: username
    """
    with engine.connect() as connection:
        try:
            result = connection.execute(text("DELETE FROM users WHERE name = :name"), {"name": name})
            connection.commit()
            if result.rowcount == 0:
                print(f"User '{name}' does not exist.")
            elif result.rowcount > 0:
                print(f"User '{name}' deleted successfully.")
        except Exception as e:
            print(f"Error: {e}")
