import movies_storage.movies_storage_sql as storage
import movies
from config import shared_data as sd

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'


def print_user_profiles_menu():
    """
    Prints the user profiles
    """
    # user_selected = int()
    user_profiles = storage.list_users().fetchall()
    user_profiles_dict = {}
    number = 1
    for user in user_profiles:
        user_profiles_dict.update({number: {"id": user[0], "name": user[1]}})
        number += 1
    user_profiles_dict.update({number: {"id": 0, "name": "Create a new user"}})

    # Menu
    print("Welcome to the Movie App! \n")
    print("Select a user:")
    for number, user in user_profiles_dict.items():
        print(f"{GREEN}{number}. {user["name"]}{RESET}")
    print("")
    while True:
        try:
            user_selected = input("")
            if user_selected == "" or int(user_selected) not in user_profiles_dict.keys():
                raise ValueError(f"{RED}Please select a valid user through number.{RESET}")
            elif user_profiles_dict.get(int(user_selected)).get("name") == "Create a new user":
                new_username = input("Please enter a username: ")
                if new_username == "" or new_username is None:
                    raise ValueError(f"{RED}New user name can not be empty.{RESET}")
                else:
                    storage.add_user(new_username)
                    print(f"{GREEN}Restart the program to activate the new user.{RESET}")
                    movies.command_exit()
            else:
                sd.update({"active_user_id": user_profiles_dict.get(int(user_selected)).get("id"),
                           "name": user_profiles_dict.get(int(user_selected)).get("name")})
            break
        except ValueError as e:
            print(e)
