import functools
import os
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init as colorama_init

from filmweb import filmweb
from filmweb.base import Movie, initialize_csv, export_file, want_to_see_file, favorites_file
from filmweb.filmweb import FilmwebPage, get_pages_count, scrape_multithreaded

colorama_init()

parser = ArgumentParser(
    description="Export Filmweb's ratings to a TMDB compatible csv file.")
parser.add_argument("--username", type=str, metavar="<user>",
                    help="Filmweb username")
parser.add_argument("--token", type=str, metavar="<token>",
                    help="Filmweb token cookie")
parser.add_argument("--session", type=str, metavar="<session>",
                    help="Filmweb session cookie")
parser.add_argument("--jwt", type=str, metavar="<jwt>",
                    help="Filmweb JSON Web Token")
parser.add_argument("--threads", type=int, metavar="<threads>",
                    default=5, help="Number of threads to create. Default: 5")
parser.add_argument("-i", action="store_true", help="interactive mode")
parser.add_argument("--force_chrome", action="store_true",
                    help="Force Chrome (interactive mode only)")
parser.add_argument("--force_firefox", action="store_true",
                    help="Force Firefox (interactive mode only)")
parser.add_argument("--page_start", type=int, metavar="<page>",
                    help="Start from X filmweb page", default=1)
parser.add_argument("--debug", action="store_true",
                    help="Show error messages")
args = parser.parse_args()


def filmweb_export(username):
    f_pages, s_pages, w_pages = get_pages_count(username)
    if not args.debug:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            executor.map(functools.partial(scrape_multithreaded, username, "films"), list(range(1, f_pages + 1)))
            executor.map(functools.partial(scrape_multithreaded, username, "serials"), list(range(1, s_pages + 1)))
            executor.map(functools.partial(scrape_multithreaded, username, "wantToSee"), list(range(1, w_pages + 1)))
    else:  # this thing definitely needs to be UwUed edit: rewritten to rust*
        for page in list(range(1, f_pages + 1)):
            scrape_multithreaded(username, "films", page)
        for page in list(range(1, s_pages + 1)):
            scrape_multithreaded(username, "serials", page)
        for page in list(range(1, w_pages + 1)):
            scrape_multithreaded(username, "wantToSee", page)

    print(f"Exported {Movie.found_titles_count} titles")
    print(f"Films, Serials: {os.path.abspath(export_file)}")
    print(f"Favorited titles {os.path.abspath(favorites_file)}")
    print(f"Watchlist: {os.path.abspath(want_to_see_file)}")

    if Movie.not_found_titles:
        print("Following movies/serials were not found:")
        for title in Movie.not_found_titles:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} {title}")


def main():
    print("filmweb-export!")
    initialize_csv()
    if args.i:
        filmweb.login(args.force_chrome, args.force_firefox)
    if filmweb.set_cookies(args.token, args.session, args.jwt):
        if args.username:
            filmweb_export(args.username)
        else:
            filmweb_export(FilmwebPage.get_username())


if __name__ == "__main__":
    main()
