import re
import csv
import requests
from colorama import Fore, Style
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from argparse import ArgumentParser


parser = ArgumentParser(
    description="Export Filmweb's ratings to a TMDB compatible csv file.")
parser.add_argument("-s", "--session", type=str, required=True,
                    metavar="", help="Filmweb Session Cookie")
parser.add_argument("-u", "--username", type=str, metavar="",
                    required=True, help="Filmweb Username Cookie Value")
parser.add_argument("-t", "--token", type=str, metavar="",
                    required=True, help="Filmweb Token Cookie Value")
parser.add_argument("-f", "--firefox", type=str,
                    metavar="", help="Firefox binary location")
parser.add_argument("-d", "--debugging", action='store_true',
                    help="Enable debugging")
args = parser.parse_args()

cookies = {
    "_fwuser_logged": "1",
    "_fwuser_token": args.token,
    "_fwuser_sessionId": args.session
}

options = webdriver.FirefoxOptions()

if not args.debugging:
    options.add_argument('--headless')

driver = webdriver.Firefox(firefox_binary=(args.firefox), options=options)
driver.implicitly_wait(10)

current_date = datetime.now().strftime("%d-%m-%Y-%H:%M:%S")

fieldnames = ["Position", "Const", "Created", "Modified", "Description",
              "Title", "URL", "Title Type", "IMDb Rating", "Runtime (mins)",
              "Year", "Genres", "Num Votes", "Release Date", "Directors",
              "Your Rating", "Date Rated"]


# program itself


class Movie:
    def __init__(self, title, orig_title, year, rating, imdb_id):
        self.title = title
        self.orig_title = orig_title
        self.year = year
        self.rating = rating
        self.imdb_id = imdb_id


def set_cookies(session, token):
    r = requests.get("https://filmweb.pl/settings", cookies=cookies)
    if "Twój adres IP" in r.text:
        print("Valid cookies")
        return True
    else:
        print(f"{Fore.RED}Invalid cookies")
        return False


def initializeCSV(date):
    with open(f"export-{date}.csv", "w", newline="") as imdb_CSV:
        writer = csv.DictWriter(imdb_CSV, fieldnames=fieldnames)
        writer.writeheader()


def scrapeRatings(page, username):
    done_scraping = False
    titles = []
    years = []
    ratings = []
    const = []
    type = "films"

    r = requests.get(f"https://filmweb.pl/user/{username}/{type}?page={page}", cookies=cookies)
    if "emptyContent" in r.text:
        if type == "films":
            type = "serials"
            r = requests.get(f"https://filmweb.pl/user/{username}/{type}?page={page}", cookies=cookies)
        else:
            done_scraping = True

    if done_scraping is True:
        print(f"Export finished in export-{current_date}.csv")
    else:
        soup = BeautifulSoup(r.text, "lxml")

        titles_amount = len(soup.find_all(class_="filmPreview__title"))
        print(f"Scraping {titles_amount} {type} from page {page}")

        for i in range(0, titles_amount):
            vote_box = soup.find(class_="myVoteBox__mainBox").extract()
            polish_title = vote_box.find(class_=("filmPreview__title"))
            orig_title = vote_box.find(class_="filmPreview__originalTitle")
            years.append(vote_box.find(class_="filmPreview__year").text)
            ratings.append(vote_box.find(class_="userRate__rate").text)
            if orig_title is not None:
                titles.append(orig_title.text)
            else:
                titles.append(polish_title.text)
        return titles, years, ratings, const


def getImdbID(titles, years, const, rated_movies):
    movie_index = 0
    while movie_index < rated_movies:
        r = requests.get(f"https://imdb.com/search/title/?realm=title&title=\
        {titles[movie_index]}&release_date-min={years[movie_index]}\
        &release_date-max={years[movie_index]}")

        soup = BeautifulSoup(r.text, "lxml")
        try:
            film_block = soup.find(class_="lister-item-header").extract()
            imdb_id = film_block.find('a').get('href')
            const.append(re.findall(r"tt\d{7,8}", imdb_id)[0])
            print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {titles[movie_index]}")
            movie_index += 1
        except AttributeError:
            const.append("notfound")
            print(f"{Fore.RED}[-]{Style.RESET_ALL} {titles[movie_index]} not found")
            movie_index += 1
    return const


def appendRatings(const, titles, years, ratings):
    fetched_Ratings = []
    for i in range(0, len(const)):
        fetched_Ratings.append(dict({"Const": str(
            const[i]), "Title": titles[i], "Year": years[i],
            "Your Rating": ratings[i]}))
    return fetched_Ratings


def writeRows(fetched_ratings):
    with open(f"export-{current_date}.csv", "a", newline="") as imdb_csv:
        for fetched_rating in fetched_ratings:
            csv_writer = csv.DictWriter(imdb_csv, fieldnames=fieldnames)
            csv_writer.writerow(fetched_rating)


def filmweb_export(username):
    initializeCSV(current_date)
    page = 1
    done_scraping = False
    while not done_scraping:
        try:
            titles, years, ratings, const, done_scraping = scrapeRatings(page, username)
        except TypeError:  # it means scraping and export finished
            break
        const = getImdbID(titles, years, const, len(titles))

        fetched_ratings = appendRatings(const, titles, years, ratings)
        writeRows(fetched_ratings)
        page += 1


print("filmweb-export starting")
if set_cookies(args.session, args.token):
    filmweb_export(args.username)
    driver.quit()
