import re
import csv
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from argparse import ArgumentParser


# initial configuration

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


def set_cookies(session, token):
    driver.get("https://filmweb.pl")
    cookie_logged = {"name": "_fwuser_logged", "value": "1"}
    cookie_token = {"name": "_fwuser_token", "value": token}
    cookie_session = {"name": "_fwuser_sessionId", "value": session}
    driver.add_cookie(cookie_logged)
    driver.add_cookie(cookie_token)
    driver.add_cookie(cookie_session)
    driver.get("https://filmweb.pl/settings")
    if driver.current_url != "https://www.filmweb.pl/settings":
        print('Session cookie is invalid.')
        driver.quit()
        return False
    else:
        return True


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
    driver.get(
        f"https://filmweb.pl/user/{username}/films?page={page}")
    html = driver.page_source
    done_scraping = True if "oceniłeś" in html else False

    soup = BeautifulSoup(html, "lxml")

    titles_amount = len(soup.find_all(class_="filmPreview__title"))

    for i in range(0, titles_amount):
        vote_box = soup.find(class_="myVoteBox__mainBox").extract()
        znaleziony = vote_box.find(class_=("filmPreview__title"))
        years.append(vote_box.find(class_="filmPreview__year").text)
        ratings.append(vote_box.find(class_="userRate__rate").text)
        orig_title = vote_box.find(class_="filmPreview__originalTitle")
        if orig_title is not None:
            titles.append(orig_title.text)
        else:
            titles.append(znaleziony.text)
    return titles, years, ratings, const, done_scraping


def getImdbID(titles, years, const, rated_movies):
    movie_index = 0
    while movie_index < rated_movies:
        print(f"Searching for: {titles[movie_index]}")
        driver.get(
            f"https://imdb.com/search/title/?realm=title&title=\
            {titles[movie_index]} &release_date-min={years[movie_index]}\
&release_date-max={years[movie_index]}")

        while True:
            try:
                time.sleep(1)
                driver.find_element(By.XPATH, "//img[@class='loadlate']").click()
                imdb_url = driver.current_url
                const.append(re.findall(r"tt\d{7,8}", imdb_url)[0])
                movie_index += 1
            except NoSuchElementException:
                const.append("notfound")
                movie_index += 1
                break
            except IndexError as e:
                print(f"Not found ID in this url: {imdb_url} {e}")
                continue
            break
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
        titles, years, ratings, const, done_scraping = scrapeRatings(page, username)
        rated_movies = len(titles)
        print(f"Found {rated_movies} rated movies.")
        time.sleep(5)
        const = getImdbID(titles, years, const, rated_movies)

        fetched_ratings = appendRatings(const, titles, years, ratings)
        writeRows(fetched_ratings)
        page += 1


print("filmweb-export starting")
if set_cookies(args.session, args.token):
    filmweb_export(args.username)
    driver.quit()
