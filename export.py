from argparse import ArgumentParser

from filmweb import filmweb
from filmweb.base import initialize_csv


parser = ArgumentParser(
    description="Export Filmweb's ratings to a TMDB compatible csv file.")
parser.add_argument("--username", type=str, metavar="<user>",
                    help="Filmweb username")
parser.add_argument("--token", type=str, metavar="<token>",
                    help="Filmweb token cookie")
parser.add_argument("--session", type=str, metavar="<session>",
                    help="Filmweb session cookie")
parser.add_argument("-i", action="store_true", help="interactive mode")
parser.add_argument("--force_chrome", action="store_true", help="Force Chrome (interactive mode only)")
parser.add_argument("--force_firefox", action="store_true", help="Force Firefox (interactive mode only)")
args = parser.parse_args()


def filmweb_export(username):
    initialize_csv()
    page = 1
    while not filmweb.scrape(page, username, "films"):
        page += 1
    page = 1
    while not filmweb.scrape(page, username, "serials"):
        page += 1
    page = 1
    while not filmweb.scrape(page, username, "wantToSee"):
        page += 1


def main():
    print("filmweb-export!")
    if args.i:
        filmweb.login(args.force_chrome, args.force_firefox)
    if filmweb.set_cookies(args.token, args.session):
        if args.username:
            filmweb_export(args.username)
        else:
            filmweb_export(filmweb.get_username())


if __name__ == "__main__":
    main()
