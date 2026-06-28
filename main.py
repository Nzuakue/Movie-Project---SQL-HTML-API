import movies

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'


def main():
    user_choice = int()
    funct_dict = {0: movies.command_exit, 1: movies.command_list_movies, 2: movies.command_add_movie,
                  3: movies.command_delete_movie,
                  4: movies.command_update_movie, 5: movies.command_generate_stats,
                  6: movies.command_random_movie,
                  7: movies.command_search_movie, 8: movies.command_sort_by_rating, 9: movies.command_sort_by_year,
                  10: movies.command_create_histogram,
                  11: movies.command_filter_movies, 12: movies.command_generate_website
                  }
    print('********** My Movies Database **********', end='\n\n')
    while True:
        movies.menu()
        try:
            user_choice = input(f'{YELLOW}Enter choice (0-12): {RESET}')
            if not (user_choice.isdecimal() and int(user_choice) in range(0, 13)):
                raise ValueError(f"{RED}Enter a number between 0 and 12{RESET}")
            user_choice = int(user_choice)
        except ValueError as e:
            print(f"{RED}{e}{RESET}")
        else:
            funct_dict[user_choice]()
            print('')
            input(f'{YELLOW}Press enter to continue.{RESET}')
            print('')


if __name__ == '__main__':
    main()
