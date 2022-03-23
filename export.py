from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style
import functools

from filmweb import filmweb
from filmweb.base import initialize_csv, not_found_titles, current_date
from filmweb.filmweb import get_pages_count, scrape_multithreaded


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
                    default=10, help="Number of threads to create. Default: 10")
parser.add_argument("-i", action="store_true", help="interactive mode")
parser.add_argument("--force_chrome", action="store_true", help="Force Chrome (interactive mode only)")
parser.add_argument("--force_firefox", action="store_true", help="Force Firefox (interactive mode only)")
parser.add_argument("--page_start", type=int, metavar="<page>", help="Start from X filmweb page", default=1)
args = parser.parse_args()


def filmweb_export(username):
    f_pages, s_pages, w_pages = get_pages_count(username)
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        executor.map(functools.partial(scrape_multithreaded, username, "films"), list(range(1, f_pages + 1)))
        executor.map(functools.partial(scrape_multithreaded, username, "serials"), list(range(1, s_pages + 1)))
        executor.map(functools.partial(scrape_multithreaded, username, "wantToSee"), list(range(1, w_pages + 1)))

   
    # TODO: improve given paths
    print("Exporting has finished")
    print(f"./exports/export-{current_date}.csv")
    print(f"./exports/wantToSee-{current_date}.csv")
    if not_found_titles:
        print("Following movies/serials were not found:")
        for title in not_found_titles:
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
            filmweb_export(filmweb.get_username())


if __name__ == "__main__":
    main()

