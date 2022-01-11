import re
import csv
from datetime import datetime
import requests
import json
from colorama import Fore, Style
from bs4 import BeautifulSoup
from argparse import ArgumentParser


parser = ArgumentParser(
    description="Export Filmweb's ratings to a TMDB compatible csv file.")
parser.add_argument("--username", type=str, metavar="<user>",
                    required=False, help="Filmweb username")
parser.add_argument("--token", type=str, metavar="<token>",
                    required=True, help="Filmweb token cookie")
parser.add_argument("--session", type=str, metavar="<session>",
                    required=True, help="Filmweb session cookie")
args = parser.parse_args()

cookies = {
    "_fwuser_logged": "1",
    "_fwuser_token": args.token,
    "_fwuser_sessionId": args.session
}

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
        self.imdb_id = self.imdb_id_logic()
        self.writeMovie()


    def imdb_id_logic(self):
        if self.translated:
            if (imdb := self.get_imdb_id(self.orig_title, self.year, True)) != False:
                print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {self.title}")
                return imdb
            elif (imdb := self.get_imdb_id(self.title, self.year, True)) != False:
                print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {self.title}")
                return imdb
            elif (imdb := self.get_imdb_id(self.title, self.year, False)) != False:
                print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {self.title}")
                return imdb
            else:
                print(f"{Fore.RED}[-]{Style.RESET_ALL} {self.title} not found")
                return "not-found"
        elif (imdb := self.get_imdb_id(self.title, self.year, True)) != False:
            print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {self.title}")
            return imdb
        else:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} {self.title} not found")
            return "not-found"


    def get_imdb_id(self, title, year, advanced_search):
        if advanced_search == True:
            url = f"https://imdb.com/search/title/?realm=title&title=\
                    {title}&release_date-min={year}&release_date-max={year}"
            html_class = "lister-item-header"
        else:
            url = f"https://www.imdb.com/find?q={title}"
            html_class = "result_text"

        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")

        try:
            film_block = soup.find(class_=html_class).extract()
            imdb_id = film_block.find("a").get("href")
            imdb_id = re.findall(r"tt\d{7,8}", imdb_id)[0]
            return imdb_id
        except AttributeError:
            return False


    def writeMovie(self):
        with open(f"export-{current_date}.csv", "a", newline="", encoding="utf-8") as imdb_csv:
            csv_writer = csv.DictWriter(imdb_csv, fieldnames=fieldnames)
            csv_writer.writerow({"Const": self.imdb_id, "Title": self.orig_title if self.translated is True else self.title, "Year": self.year,
                                 "Your Rating": self.rating})


def check_cookies():
    r = requests.get("https://filmweb.pl/settings", cookies=cookies)
    if "Twój adres IP" in r.text:
        print("Valid cookies")
        return True
    else:
        print(f"{Fore.RED}Invalid cookies")
        return False


def get_username():
    r = requests.get("https://filmweb.pl/settings", cookies=cookies)
    soup = BeautifulSoup(r.text, "lxml")
    return soup.find(class_="userAvatar__image").attrs["alt"]


def initialize_csv(date):
    with open(f"export-{date}.csv", "w", newline="", encoding="utf-8") as imdb_csv:
        writer = csv.DictWriter(imdb_csv, fieldnames=fieldnames)
        writer.writeheader()


def scrapeRatings(page, username, title_type):
    r = requests.get(f"https://filmweb.pl/user/{username}/{title_type}?page={page}", cookies=cookies)
    if "emptyContent" in r.text:
        if type == "serials":
            print(f"Export finished in export-{current_date}.csv")
            return True
        else:
            return True

    soup = BeautifulSoup(r.text, "lxml")
    titles_amount = len(soup.find_all(class_="myVoteBox__mainBox"))
    print(f"Scraping {titles_amount} {title_type} from page {page}")
    scripts = soup.find("span", class_="dataSource").extract()
    i = 1
    while i <= titles_amount:
        vote_box = soup.find(class_="myVoteBox__mainBox").extract()
        title = vote_box.find(class_="filmPreview__title").text
        orig_title = vote_box.find(class_="filmPreview__originalTitle")
        translated = False if orig_title is None else True
        year = vote_box.find(class_="filmPreview__year").text
        rating = scripts.find("script").extract().text
        rating = json.loads(rating)["r"]
        Movie(title, orig_title, year, rating, translated)
        i+=1


def filmweb_export(username):
    initialize_csv(current_date)

    page = 1
    while not scrapeRatings(page, username, "films"):
        page += 1

    page = 1
    while not scrapeRatings(page, username, "serials"):
        page += 1


print("filmweb-export!")
if check_cookies():
    if args.username:
        filmweb_export(args.username)
    else:
        filmweb_export(get_username())