import requests
import re
from bs4 import BeautifulSoup
from colorama import Fore, Style


def imdb_id_logic(self):
    if (imdb := get_imdb_id(self.orig_title, self.year, True)) and self.translated or\
       (imdb := get_imdb_id(self.title, self.year, True)) or\
       (imdb := get_imdb_id(self.title, self.year, False)):
        print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {self.title}")
        return imdb
    else:
        print(f"{Fore.RED}[-]{Style.RESET_ALL} {self.title} not found")
        return "not-found"


def get_imdb_id(title, year, advanced_search):
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
    except AttributeError:
        return False
