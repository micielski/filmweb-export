from bs4 import BeautifulSoup
from colorama import Fore, Style
from datetime import datetime
import csv
import os
import re
import requests

FIELDNAMES = ["Const", "Your Rating", "Date Rated", "Title", "URL",
              "Title Type", "IMDb Rating", "Runtime (mins)", "Year",
              "Genres", "Num Votes", "Release Date", "Directors"]

current_date = datetime.now().strftime("%d-%m-%Y-%H:%M")
not_found_titles = []

class Movie:
    def __init__(self, title, orig_title, year, rating, translated, title_type):
        self.title = title
        self.title_type = title_type
        self.year = year
        self.rating = rating if title_type != "wantToSee" else None
        self.translated = translated
        self.orig_title = orig_title.text if translated else None
        self.imdb_id = self.imdb_id_logic()
        self.write_movie()

        if self.imdb_id == "not-found":
            not_found_titles.append(self.title)
            

    def imdb_id_logic(self):
        if self.translated and (imdb := self.get_imdb_id(self.orig_title, self.year, True)) or\
           (imdb := self.get_imdb_id(self.title, self.year, True)) or\
           (imdb := self.get_imdb_id(self.title, self.year, False)):
            print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {self.title}")
            return imdb
        else:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} {self.title} not found")
            return "not-found"

    def get_imdb_id(self, title, year, advanced_search):
        if advanced_search:
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
        except (AttributeError, IndexError):
            return False

    def write_movie(self):
        filename = f"exports/export-{current_date}.csv" if self.title_type != "wantToSee" else f"exports/wantToSee-{current_date}.csv"
        with open(filename, "a", newline="", encoding="utf-8") as imdb_csv:
            csv_writer = csv.DictWriter(imdb_csv, fieldnames=FIELDNAMES)
            csv_writer.writerow({"Const": self.imdb_id, "Title": self.orig_title if self.translated is True else self.title,
                                "Year": self.year, "Your Rating": self.rating})


def initialize_csv():
    try:
        os.mkdir('exports')
    except FileExistsError:
        pass
    with open(f"exports/export-{current_date}.csv", "w", newline="", encoding="utf-8") as export,\
         open(f"exports/wantToSee-{current_date}.csv", "w", newline="", encoding="utf-8") as want_to_see:
        csv.DictWriter(export, fieldnames=FIELDNAMES).writeheader()
        csv.DictWriter(want_to_see, fieldnames=FIELDNAMES).writeheader()
