import re
import csv
import requests
from colorama import Fore, Style
from datetime import datetime
from bs4 import BeautifulSoup
#from selenium import webdriver
from argparse import ArgumentParser


parser = ArgumentParser(
    description="Export Filmweb's ratings to a TMDB compatible csv file.")
parser.add_argument("--username", type=str, metavar="<user>",
                    required=True, help="Filmweb username")
parser.add_argument("--token", type=str, metavar="<token>",
                    required=True, help="Filmweb token cookie")
parser.add_argument("--session", type=str, metavar="<session>", required=True,
                    help="Filmweb session cookie")
# parser.add_argument("-f", "--firefox", type=str,
#                     metavar="", help="Firefox binary location")
# parser.add_argument("-d", "--debugging", action='store_true',
#                     help="Enable debugging")
args = parser.parse_args()

cookies = {
    "_fwuser_logged": "1",
    "_fwuser_token": args.token,
    "_fwuser_sessionId": args.session
}

#options = webdriver.FirefoxOptions()

#if not args.debugging:
#    options.add_argument('--headless')

#driver = webdriver.Firefox(firefox_binary=(args.firefox), options=options)
#driver.implicitly_wait(10)

current_date = datetime.now().strftime("%d-%m-%Y-%H:%M:%S")

fieldnames = ["Const", "Your Rating", "Date Rated", "Title", "URL",
              "Title Type", "IMDb Rating", "Runtime (mins)", "Year",
              "Genres", "Num Votes", "Release Date", "Directors"]


class Movie:
    def __init__(self, title, orig_title, year, rating, translated):
        self.title = title
        self.year = year
        self.rating = rating
        self.translated = translated
        if translated:
            self.orig_title = orig_title.text
        else:
            self.orig_title = None
        self.imdb_id = self.getImdbID()
        self.writeMovie()

    def getImdbID(self):
        if self.translated: # title is translated to polish on filmweb
            r = requests.get(f"https://imdb.com/search/title/?realm=title&title=\
            {self.orig_title}&release_date-min={self.year}\
            &release_date-max={self.year}")
            soup = BeautifulSoup(r.text, "lxml")
            try:
                film_block = soup.find(class_="lister-item-header").extract()
                imdb_id = film_block.find('a').get('href')
                imdb_id = re.findall(r"tt\d{7,8}", imdb_id)[0]
                print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {self.orig_title}")
                return imdb_id
            except AttributeError: # original movie title not found, fallback to polish title
                print(f"{Fore.YELLOW}[/]{Style.RESET_ALL} {self.orig_title} not found, fallback to the Polish title")
                r = requests.get(f"https://imdb.com/search/title/?realm=title&title=\
                {self.title}&release_date-min={self.year}\
                &release_date-max={self.year}")
                soup = BeautifulSoup(r.text, "lxml")
                try:
                    film_block = soup.find(class_="lister-item-header").extract()
                    imdb_id = film_block.find('a').get('href')
                    imdb_id = re.findall(r"tt\d{7,8}", imdb_id)[0]
                    print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {self.title}")
                    return imdb_id
                except AttributeError:
                    print(f"{Fore.RED}[-]{Style.RESET_ALL} {self.title} not found")
                    return "not-found"
        else: # title isn't translated to polish on filmweb
            r = requests.get(f"https://imdb.com/search/title/?realm=title&title=\
            {self.orig_title}&release_date-min={self.year}\
            &release_date-max={self.year}")
            soup = BeautifulSoup(r.text, "lxml")
            try:
                film_block = soup.find(class_="lister-item-header").extract()
                imdb_id = film_block.find('a').get('href')
                imdb_id = re.findall(r"tt\d{7,8}", imdb_id)[0]
                print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {self.title}")
                return imdb_id
            except AttributeError:
                print(f"{Fore.RED}[-]{Style.RESET_ALL} {self.title} not found")
                return "not-found"

    def writeMovie(self):
        with open(f"export-{current_date}.csv", "a", newline="") as imdb_csv:
            csv_writer = csv.DictWriter(imdb_csv, fieldnames=fieldnames)
            csv_writer.writerow({'Const': self.imdb_id, 'Title': self.orig_title, 'Year': self.year,
                                 'Your Rating': self.rating})


def set_cookies(session, token):
    r = requests.get("https://filmweb.pl/settings", cookies=cookies)
    if "Twój adres IP" in r.text:
        print("Valid cookies")
        return True
    else:
        print(f"{Fore.RED}Invalid cookies")
        return False


def get_username():
    pass


def initialize_csv(date):
    with open(f"export-{date}.csv", "w", newline="") as imdb_CSV:
        writer = csv.DictWriter(imdb_CSV, fieldnames=fieldnames)
        writer.writeheader()


def scrapeRatings(page, username, type):
    r = requests.get(f"https://filmweb.pl/user/{username}/{type}?page={page}", cookies=cookies)
    if "emptyContent" in r.text:
        if type == "serials":
            print(f"Export finished in export-{current_date}.csv")
            return True
        else:
            return True

    soup = BeautifulSoup(r.text, "lxml")
    titles_amount = len(soup.find_all(class_="myVoteBox__mainBox"))
    print(f"Scraping {titles_amount} {type} from page {page}")

    for i in range(0, titles_amount):
        vote_box = soup.find(class_="myVoteBox__mainBox").extract()
        title = vote_box.find(class_="filmPreview__title").text
        orig_title = vote_box.find(class_="filmPreview__originalTitle")
        translated = False if orig_title is None else True
        year = vote_box.find(class_="filmPreview__year").text
        rating = vote_box.find(class_="userRate__rate").text
        Movie(title, orig_title, year, rating, translated)


def filmweb_export(username):
    initialize_csv(current_date)
    page = 1
    while not scrapeRatings(page, username, "films"):
        page += 1
    page = 1
    while not scrapeRatings(page, username, "serials"):
        page += 1


print("filmweb-export!")
if set_cookies(args.session, args.token):
    filmweb_export(args.username)
