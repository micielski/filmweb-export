import csv
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style


FIELDNAMES = ["Const", "Your Rating", "Date Rated", "Title", "URL",
              "Title Type", "IMDb Rating", "Runtime (mins)", "Year",
              "Genres", "Num Votes", "Release Date", "Directors"]

current_date = datetime.now().strftime("%d-%m-%Y-%H:%M")
favorites_file = f"exports/favorites-{current_date}.csv"
export_file = f"exports/export-{current_date}.csv"
want_to_see_file = f"exports/wantToSee-{current_date}.csv"


class Movie:
    not_found_titles = []
    found_titles_count = 0

    def __init__(self, title: str, orig_title: str, year: int, title_type: str, rating: int, is_favorite: bool):
        assert year > 1873, "Year should not be lower than 1874"

        self.title = title
        self.title_type = title_type
        self.year = year
        self.rating = rating if title_type != "wantToSee" else None
        self.translated = bool(orig_title)
        self.orig_title = orig_title
        self.is_favorite = is_favorite
        self.imdb_id = self.imdb_id_logic()
        self.write_movie_logic()

        if self.imdb_id == "not-found":
            Movie.not_found_titles.append(self.title)

    def write_movie_logic(self):
        if self.is_favorite:
            self.write_movie("favorites")
        elif self.title_type != "wantToSee":
            self.write_movie("export")
        else:
            self.write_movie("wantToSee")

    def imdb_id_logic(self):
        if self.translated and \
           (imdb := self.get_imdb_id(self.orig_title, True)) or \
           (imdb := self.get_imdb_id(self.title, True)) or \
           (imdb := self.get_imdb_id(self.title, False)):
            print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {self.title}")
            return imdb
        print(f"{Fore.RED}[-]{Style.RESET_ALL} {self.title}")
        return "not-found"

    def get_imdb_id(self, title, advanced_search):
        if advanced_search:
            url = f"https://imdb.com/search/title/?realm=title&title= \
                    {title}&release_date-min={self.year}&release_date-max= \
                    {self.year}"
            html_class = "lister-item-header"
        else:
            url = f"https://www.imdb.com/find?q={title}"
            html_class = "result_text"

        page_source = requests.get(url).text
        soup = BeautifulSoup(page_source, "lxml")

        try:
            film_block = soup.find(class_=html_class).extract()
            imdb_id = film_block.find("a").get("href")
            imdb_id = re.findall(r"tt\d{7,8}", imdb_id)[0]
            Movie.found_titles_count += 1
            return imdb_id
        except (AttributeError, IndexError):
            return False

    def write_movie(self, name: str):
        filename = f"exports/{name}-{current_date}.csv"
        with open(filename, "a", newline="", encoding="utf-8") as imdb_csv:
            csv_writer = csv.DictWriter(imdb_csv, fieldnames=FIELDNAMES)
            csv_writer.writerow({"Const": self.imdb_id, "Title": self.orig_title if self.translated
                                else self.title, "Year": self.year, "Your Rating": self.rating})


def initialize_csv():
    try:
        os.mkdir('exports')
    except FileExistsError:
        pass
    with open(export_file, "w", newline="", encoding="utf-8") as export,\
            open(want_to_see_file, "w", newline="", encoding="utf-8") as want_to_see,\
            open(favorites_file, "w", newline="", encoding="utf-8") as favorites:
        csv.DictWriter(export, fieldnames=FIELDNAMES).writeheader()
        csv.DictWriter(want_to_see, fieldnames=FIELDNAMES).writeheader()
        csv.DictWriter(favorites, fieldnames=FIELDNAMES).writeheader()
