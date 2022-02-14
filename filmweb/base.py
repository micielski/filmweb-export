from datetime import datetime
import csv
from filmweb.imdb import imdb_id_logic

FIELDNAMES = ["Const", "Your Rating", "Date Rated", "Title", "URL",
              "Title Type", "IMDb Rating", "Runtime (mins)", "Year",
              "Genres", "Num Votes", "Release Date", "Directors"]
cookies = {
    "_fwuser_logged": "1",
    "_fwuser_token": None,
    "_fwuser_sessionId": None
}
current_date = datetime.now().strftime("%d-%m-%Y-%H:%M")


class Movie:
    def __init__(self, title, orig_title, year, rating, translated, title_type):
        self.title = title
        self.title_type = title_type
        self.year = year
        self.rating = rating if title_type != "wantToSee" else None
        self.translated = translated
        self.orig_title = orig_title.text if translated else None
        self.imdb_id = imdb_id_logic(self)
        self.write_movie()

    def write_movie(self):
        filename = f"export-{current_date}.csv" if self.title_type != "wantToSee" else f"wantToSee-{current_date}.csv"
        with open(filename, "a", newline="", encoding="utf-8") as imdb_csv:
            csv_writer = csv.DictWriter(imdb_csv, fieldnames=FIELDNAMES)
            csv_writer.writerow({"Const": self.imdb_id, "Title": self.orig_title if self.translated is True else self.title,
                                "Year": self.year, "Your Rating": self.rating})


def initialize_csv():
    with open(f"export-{current_date}.csv", "w", newline="", encoding="utf-8") as export,\
         open(f"wantToSee-{current_date}.csv", "w", newline="", encoding="utf-8") as want_to_see:
        csv.DictWriter(export, fieldnames=FIELDNAMES).writeheader()
        csv.DictWriter(want_to_see, fieldnames=FIELDNAMES).writeheader()
