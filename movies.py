import statistics as st
import random as rand
from operator import itemgetter
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from rapidfuzz import fuzz
import movie_storage.movie_storage_sql as storage
import sys
import movies_content_generator as mcg

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'

# Load .env file
load_dotenv()


def menu():
    menu_options = ['Exit', 'List movies', 'Add movie', 'Delete movie'
        , 'Update movie', 'Statistics', 'Random movie', 'Search movie'
        , 'Movies sorted by rating', "Movies sorted by year", 'Create rating histogram', 'Filter movies',
                    "Generate website"]
    print('Menu:')
    for option in menu_options:
        print(f'{GREEN}{menu_options.index(option)}: {option}{RESET}')
    print('')


def input_movie_properties(input_text, return_type):
    """Get safely movie title, year and rates from user"""
    error_message = ""
    while True:
        try:
            user_input = input(input_text)
            if return_type == "str" and len(user_input) == 0:
                raise ValueError('Movie name is empty or contains only space!')
            elif return_type == "float":
                return float(user_input)
            elif return_type == "int":
                return int(user_input)
            else:
                return user_input
        except ValueError as e:
            error_message = str(e)
        if 'Movie name is empty' in error_message:
            print(f"{RED}{error_message}{RESET}")
        elif "could not convert string to float" in error_message:
            print(f"{RED}Enter a valid rate{RESET}")
        elif "invalid literal for int() with base 10" in error_message:
            print(f"{RED}Enter a valid year{RESET}")


def command_list_movies():
    """Print all movies from the database"""
    movies = storage.list_movies().fetchall()
    print(f'{len(movies)} movies in total')
    for movie in movies:
        print(f'{movie.title} ({movie.year}): {movie.rating}')


def command_add_movie():
    """Add a movie to the database if it doesn't exist"""
    title = input_movie_properties("Enter a movie title: ", 'str')
    storage.add_movie(title)


def command_delete_movie():
    """Delete a movie in the database if it exists"""
    title = input_movie_properties("Enter a movie name: ", 'str')
    storage.delete_movie(title)


def command_update_movie():
    """Update a movie in the database if it exists"""
    title = input_movie_properties("Enter a movie name: ", 'str')
    rate = input_movie_properties("Enter a movie rate: ", 'float')
    storage.update_movie(title, rate)


def command_generate_stats():
    """Print statistics (mean, median best and worst movies) of movies in the database"""
    # Get all movies and rates from database
    all_movies_and_rates = {}
    for row in storage.list_movies().fetchall():
        all_movies_and_rates.update({row.title: row.rating})
    # Average rating
    print(f'The average rating is {st.mean(list(all_movies_and_rates.values())): .1f}')
    # Median rating
    print(f'The median rating is {st.median(list(all_movies_and_rates.values())): .1f}')

    # Best movies based on rating
    max_rate = max(list(all_movies_and_rates.values()))
    best_movies = set()
    for movie, rate in all_movies_and_rates.items():
        if rate == max_rate:
            best_movies.add(movie)
    print('Best movies:', end=' ')
    for movie in best_movies:
        if movie == list(best_movies)[-1]:
            print(movie)
        else:
            print(movie, end=", ")

    # Worst movies based on rating
    min_rate = min(list(all_movies_and_rates.values()))
    worst_movies = set()
    for movie, rate in all_movies_and_rates.items():
        if rate == min_rate:
            worst_movies.add(movie)
    print('Worst movies:', end=' ')
    for movie in worst_movies:
        if movie == list(worst_movies)[-1]:
            print(movie)
        else:
            print(movie, end=", ")


def command_random_movie():
    """Generate a random movie from the database"""
    # Get all movies and rates from database
    all_movies_and_rates = {}
    for row in storage.list_movies().fetchall():
        all_movies_and_rates.update({row.title: row.rating})
    movie = rand.choice(list(all_movies_and_rates.items()))
    print(f'{movie[0]}: {movie[1]}')


def command_search_movie():
    """Search for a movie from the database"""
    movies_found = {}
    while True:
        try:
            title = input(f'{YELLOW}Enter the movie name: {RESET}')
            if title == "": raise ValueError('Movie name cannot be empty')
            break
        except ValueError as e:
            print(e)
    for row in storage.list_movies().fetchall():
        if row.title.lower() == title.lower():
            print(f'{row.title}: {row.rating}')
            break
        elif row.title.lower() != title.lower():
            score = fuzz.partial_ratio(title.lower(), row.title.lower())
            if score >= 80:
                movies_found.update({row.title: row.rating})
    if len(movies_found) > 0:
        print(f'The movie {RED}"{title}"{RESET} does not exist. Did you mean:')
        for movie, rate in movies_found.items():
            print(f'{movie}: {rate}')
    elif not (len(movies_found) == 0 and title.lower() == row.title.lower()):
        print(f'The movie {RED}"{title}"{RESET} does not exist.')


def command_sort_by_rating():
    """Sort the movies by the rating in descending order"""
    sorted_movies = []
    sorted_movies = sorted(storage.list_movies().fetchall(), key=itemgetter(2), reverse=True)
    for movie in sorted_movies:
        print(f'{movie[0]} ({movie[1]}): {movie[2]}')


def command_sort_by_year():
    """Sort the movies by the year in descending or ascending order based on user input"""
    sorted_movies = []
    while True:
        try:
            display_order = input(
                f"{YELLOW}Enter {GREEN}latest{RESET} {YELLOW}to see movies in descending order or {RESET} {GREEN}last{RESET} {YELLOW} in ascending one: {RESET}")
            if display_order == "":
                raise ValueError('Enter latest or last')
            break
        except ValueError as e:
            print(f"{RED}{e}{RESET}")
    if display_order == "latest":
        sorted_movies = sorted(storage.list_movies().fetchall(), key=itemgetter(1), reverse=True)
    elif display_order == "last":
        sorted_movies = sorted(storage.list_movies().fetchall(), key=itemgetter(1))
    for movie in sorted_movies:
        print(f'{movie[0]} ({movie[1]}): {movie[2]}')


def command_create_histogram():
    """Create a histogram of the rating of movies"""
    rates = []
    for row in storage.list_movies().fetchall():
        rates.append(row.rating)
    plt.hist(rates, bins=2, edgecolor='black')
    file_name = input(f'{YELLOW}Enter the file name: {RESET}')
    plt.savefig(file_name)
    plt.show()


def command_filter_movies():
    """Filter movies based on user criteria (minimum rate, start and end year or blank input)"""
    movies_filtered = {}
    while True:
        try:
            minimum_rate = input(f'{YELLOW}Enter minimum rate for movie: {RESET}')
            if not (minimum_rate == "" or (
                    minimum_rate.replace(".", "").isdecimal() and isinstance(float(minimum_rate), float))):
                raise ValueError("Enter decimal number or leave the input blank.")
            break
        except ValueError as e:
            print(f"{RED}{e}{RESET}")
    while True:
        try:
            start_year = input(f'{YELLOW}Enter start year for movie: {RESET}')
            if not (start_year == "" or (start_year.isdecimal() and isinstance(int(start_year), int))):
                raise ValueError("Enter start year in format YYYY or leave the input blank.")
            break
        except ValueError as e:
            print(f"{RED}{e}{RESET}")
    while True:
        try:
            end_year = input(f'{YELLOW}Enter end year for movie: {RESET}')
            if not (end_year == "" or (end_year.isdecimal() and isinstance(int(end_year), int))):
                raise ValueError("Enter end year in format YYYY or leave the input blank")
            break
        except ValueError as e:
            print(f"{RED}{e}{RESET}")

    # Filter movies based on following criteria:
    #  1. Rate is blank or minimum
    #  2. Year is blank or start year
    #  3. Year is blank or end year
    for row in storage.list_movies().fetchall():
        if minimum_rate == '' or row.rating >= float(minimum_rate):
            if start_year == '' or row.year >= int(start_year):
                if end_year == '' or row.year <= int(end_year):
                    movies_filtered.update({row.title: {"year": row.year, "rating": row.rating}})
    for movie, values in movies_filtered.items():
        print(f'{movie} ({values["year"]}): {values["rating"]}')


def command_generate_website():
    """
    Generate a website displaying all the movies in the database.
    """
    with open("_static/index.html", "w") as f:
        f.write(
            mcg.load_template_file().replace("__TEMPLATE_TITLE__", "My movies app").replace("__TEMPLATE_MOVIE_GRID__",
                                                                                            mcg.create_content()))
    print("Website was generated successfully")


def command_exit():
    sys.exit("Bye!")
