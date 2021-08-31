import re
import csv
from bs4 import BeautifulSoup  # type: ignore
from selenium import webdriver  # type: ignore
from argparse import ArgumentParser

parser = ArgumentParser(
    description="Export Filmweb's ratings to a TMDB compatible csv file.")
parser.add_argument("-s", "--session", type=str, required=True,
                    metavar="", help="Filmweb Session Cookie")
parser.add_argument("-u", "--username", type=str, metavar="",
                    required=True, help="Filmweb Username")
parser.add_argument("-f", "--firefox", type=str,
                    metavar="", help="Firefox binary location")
args = parser.parse_args()
driver = webdriver.Firefox(firefox_binary=(args.firefox))
driver.implicitly_wait(30)


def set_cookies(session):
    driver.get("https://filmweb.pl")
    cookie_logged = {"name": "_fwuser_logged", "value": "1"}
    cookie_session = {"name": "_fwuser_sessionId", "value": session}
    driver.add_cookie(cookie_logged)
    driver.add_cookie(cookie_session)
    driver.get("https://filmweb.pl/settings")
    if driver.current_url != "https://www.filmweb.pl/settings":
        print("session cookie is invalid")
        return False
    else:
        return True


def filmweb_export(username):
    done = False
    titles = []
    years = []
    ratings = []
    const = []
    p = 1
    while done is not True:
        driver.get("https://filmweb.pl/user/"
                   + username + "/films?page=" + str(p))
        p += 1

        html = driver.page_source
        done = True if "oceniłeś" in html else False
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
        fetched_Ratings = []

    i = 0
    rated_movies = len(titles)
    while i < rated_movies:
        driver.get("https://imdb.com/search/title/")
        print("Searching for: " + titles[i])
        driver.find_element_by_xpath(
            "/html/body/div[4]/div/div[2]/div[3]/form/div/div[1]/div[2]/input").send_keys(titles[i])
        driver.find_element_by_name("release_date-min").send_keys(years[i])
        driver.find_element_by_name("release_date-max").send_keys(years[i])
        driver.find_element_by_xpath(
            "/html/body/div[4]/div/div[2]/div[3]/form/div/p[3]/button").click()
        try:
            driver.find_element_by_class_name("loadlate").click()
            imdb_url = driver.current_url
            const.append(re.findall(r"tt\d{7,8}", imdb_url)[0])
        except IndexError:
            print(titles[i] + " Not Found. Skipping")
            const.append("notfound")
        i += 1

    for i in range(0, len(const)):
        fetched_Ratings.append(dict({"Const": str(
            const[i]), "Title": titles[i], "Year": years[i], "Your Rating": ratings[i]}))
    with open("export.csv", "w", newline="") as imdb_CSV:
        fieldnames = ["Position", "Const", "Created", "Modified", "Description", "Title", "URL", "Title Type", "IMDb Rating",
                      "Runtime (mins)", "Year", "Genres", "Num Votes", "Release Date", "Directors", "Your Rating", "Date Rated"]
        writer = csv.DictWriter(imdb_CSV, fieldnames=fieldnames)
        writer.writeheader()
        for fetched_Rating in fetched_Ratings:
            writer.writerow(fetched_Rating)


if set_cookies(args.session):
    filmweb_export(args.username)
