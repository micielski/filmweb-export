import re
import csv
from datetime import datetime
import requests
import json
import time
import os
import sys
from colorama import Fore, Style
from bs4 import BeautifulSoup
from argparse import ArgumentParser


parser = ArgumentParser(
    description="Export Filmweb's ratings to a TMDB compatible csv file.")
parser.add_argument("--username", type=str, metavar="<user>",
                    help="Filmweb username")
parser.add_argument("--token", type=str, metavar="<token>",
                    help="Filmweb token cookie")
parser.add_argument("--session", type=str, metavar="<session>",
                    help="Filmweb session cookie")
parser.add_argument("-i", action="store_true", help="interactive mode")
parser.add_argument("--chrome", action="store_true", help="Force Chrome browser (only for interactive mode)")
parser.add_argument("--firefox", action="store_true", help="Force Firefox browser (only for interactive mode)")
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
    def __init__(self, title, orig_title, year, rating, translated, title_type):
        self.title = title
        self.title_type = title_type
        self.year = year
        self.rating = rating if title_type != "wantToSee" else None
        self.translated = translated
        self.orig_title = orig_title.text if translated else None
        self.imdb_id = self.imdb_id_logic()
        self.write_movie()

    def imdb_id_logic(self):
        if (imdb := self.get_imdb_id(self.orig_title, self.year, True)) and self.translated or\
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
        except AttributeError:
            return False

    def write_movie(self):
        filename = f"export-{current_date}.csv" if self.title_type != "wantToSee" else f"wantToSee-{current_date}.csv"
        with open(filename, "a", newline="", encoding="utf-8") as imdb_csv:
            csv_writer = csv.DictWriter(imdb_csv, fieldnames=fieldnames)
            csv_writer.writerow({"Const": self.imdb_id, "Title": self.orig_title if self.translated is True else self.title,
                                "Year": self.year, "Your Rating": self.rating})


def check_cookies():
    if not cookies["_fwuser_token"]:
        print(f"{Fore.RED}No cookie \"_fwuser_token\" was provided{Style.RESET_ALL}")
        cookies["_fwuser_token"] = input("Token cookie: ")
    if not cookies["_fwuser_sessionId"]:
        print(f"{Fore.RED}No cookie \"_fwuser_sessionId\" was provided{Style.RESET_ALL}")
        cookies["_fwuser_sessionId"] = input("Session cookie: ")
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


def initialize_csv():
    with open(f"export-{current_date}.csv", "w", newline="", encoding="utf-8") as export, \
         open(f"wantToSee-{current_date}.csv", "w", newline="", encoding="utf-8") as want_to_see:
        csv.DictWriter(export, fieldnames=fieldnames).writeheader()
        csv.DictWriter(want_to_see, fieldnames=fieldnames).writeheader()


def scrape_ratings(page, username, title_type):
    r = requests.get(f"https://filmweb.pl/user/{username}/{title_type}?page={page}", cookies=cookies)
    if "emptyContent" in r.text:
        if type == "serials":
            print(f"Export finished in export-{current_date}.csv")
        return True

    soup = BeautifulSoup(r.text, "lxml")
    titles_amount = soup.find_all(class_="myVoteBox__mainBox")
    print(f"Scraping {len(titles_amount)} {title_type} from page {page}")
    scripts = soup.find("span", class_="dataSource").extract() if title_type != "wantToSee" else None
    for _ in titles_amount:
        vote_box = soup.find(class_="myVoteBox__mainBox").extract()
        title = vote_box.find(class_="filmPreview__title").text
        orig_title = vote_box.find(class_="filmPreview__originalTitle")
        translated = False if orig_title is None else True
        year = vote_box.find(class_="filmPreview__year").text
        rating = scripts.find("script").extract().text if title_type != "wantToSee" else None
        rating = json.loads(rating)["r"] if title_type != "wantToSee" else None
        Movie(title, orig_title, year, rating, translated, title_type)


def filmweb_login():
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    if args.chrome or not args.chrome and not args.firefox:
        options = ChromeOptions().add_argument("--headless")
        driver = webdriver.Chrome(options=options)
    else:
        options = FirefoxOptions().add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(15)
    driver.get("https://filmweb.pl/login")
    driver.find_element(By.ID, "didomi-notice-agree-button").click()
    driver.find_elements(By.CLASS_NAME, "authButton__text")[1].click()
    driver.find_element(By.NAME, "j_username").send_keys(input("Username: "))
    os.system("stty -echo")
    driver.find_element(By.NAME, "j_password").send_keys(input("Password: "))
    driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div/form/div[2]/ul/li[1]/button").click()
    time.sleep(5)
    os.system("stty echo")
    print("\n")
    driver.get("https://filmweb.pl/settings")
    time.sleep(5)
    try:
        cookies["_fwuser_sessionId"] = driver.get_cookie("_fwuser_sessionId")["value"]
        cookies["_fwuser_token"] = driver.get_cookie("_fwuser_token")["value"]
        return
    except TypeError:
        print("Either wrong password, or captcha popped up. Try typing in cookies manually")
        sys.exit(1)


def filmweb_export(username):
    initialize_csv()
    page = 1
    while not scrape_ratings(page, username, "films"):
        page += 1
    page = 1
    while not scrape_ratings(page, username, "serials"):
        page += 1
    page = 1
    while not scrape_ratings(page, username, "wantToSee"):
        page += 1


def main():
    print("filmweb-export!")
    if args.i:
        filmweb_login()
    if check_cookies():
        if args.username:
            filmweb_export(args.username)
        else:
            filmweb_export(get_username())


if __name__ == "__main__":
    main()
