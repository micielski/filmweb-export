import sys
import re
import csv
from bs4 import BeautifulSoup
from selenium import webdriver

p = 1


CHROMEDRIVER = "./chromedriver"

username = sys.argv[1]
token = sys.argv[2]
session = sys.argv[3]

driver = webdriver.Chrome(CHROMEDRIVER)
driver.implicitly_wait(30)

def set_cookies(token, session):
    driver.get("https://filmweb.pl")
    cookie_logged = {"name": "_fwuser_logged", "value": "1"}
    cookie_token = {"name": "_fwuser_token", "value": token }
    cookie_session = {"name": "_fwuser_sessionId", "value": session}
    driver.add_cookie(cookie_logged)
    driver.add_cookie(cookie_token)
    driver.add_cookie(cookie_session)
    driver.get("https://filmweb.pl/settings")
    if driver.current_url != "https://www.filmweb.pl/settings":
        print("Token and session combination is invalid")
        return False

def filmweb_export(username):
    done = False
    titles = []
    years = []
    ratings = []
    const = []
    p = 1
    while done != True:
        driver.get("https://filmweb.pl/user/" + username + "/films?page=" + str(p))
        p+=1

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
            if orig_title != None:
                titles.append(orig_title.text)
            else:
                titles.append(znaleziony.text)
        fetchedRatings = []

    i = 0
    rated_movies = len(titles)
    while i < rated_movies:
        driver.get("https://imdb.com/search/title/")
        print("Searching for: " + titles[i])
        driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[3]/form/div/div[1]/div[2]/input").send_keys(titles[i])
        driver.find_element_by_name("release_date-min").send_keys(years[i])
        driver.find_element_by_name("release_date-max").send_keys(years[i])
        driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[3]/form/div/p[3]/button").click()
        try:
            driver.find_element_by_class_name("loadlate").click()
            imdb_url = driver.current_url
            const.append(re.findall(r"tt\d{7,8}", imdb_url)[0])
        except:
            print(titles[i] + " Not Found. Skipping")
            const.append("notfound")
        i += 1

    for i in range(0, len(const)):
        fetchedRatings.append(dict({"Const": str(const[i]),"Title": titles[i], "Year": years[i], "Your Rating": ratings[i]}))
    
    with open("export.csv", "w", newline="") as imdbCSV:
        fieldnames = ["Position", "Const", "Created", "Modified", "Description", "Title", "URL", "Title Type", "IMDb Rating", "Runtime (mins)", "Year", "Genres", "Num Votes", "Release Date", "Directors", "Your Rating", "Date Rated"]
        writer = csv.DictWriter(imdbCSV, fieldnames=fieldnames)
        writer.writeheader()
        for fetchedRating in fetchedRatings:
            writer.writerow(fetchedRating)

if set_cookies(token, session) != False:
    filmweb_export(username)
