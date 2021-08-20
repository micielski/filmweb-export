from os import name
import configparser
import re
import time
import csv
from bs4 import BeautifulSoup
from rich import logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from rich import print
from rich.console import Console
from rich.progress import track

console = Console()
p = 1
userVariables = {}
settings = configparser.ConfigParser()
def parse_config():
    settings.read("settings.cfg")

    for i in ["chromedriver", "movies", "username", "password", "timeout", "token", "session"]:
        userVariables[i] = settings.get("settings", i)

parse_config()
driver = webdriver.Chrome(userVariables["chromedriver"])
driver.implicitly_wait(userVariables["timeout"])

def set_cookies(token, session, username, password):
    driver.get("https://filmweb.pl")
    cookie_logged = {"name": "_fwuser_logged", "value": "1"}
    cookie_token = {"name": "_fwuser_token", "value": token }
    cookie_session = {"name": "_fwuser_sessionId", "value": session}
    driver.add_cookie(cookie_logged)
    driver.add_cookie(cookie_token)
    driver.add_cookie(cookie_session)
    driver.get("https://filmweb.pl/settings")
    if driver.current_url != "https://www.filmweb.pl/settings":
        console.log("token and session invalid, performing a logging in action")
        success = filmweb_login(username, password)
        if success == 0:
            return False
        else:
            print("[green]Logged in correctly.[/green]")

def filmweb_login(username, password):
    driver.get("https://filmweb.pl/login")
    try:
        driver.find_element_by_xpath("//*[@id=\"site\"]/div[2]/div/div/div[1]/div/div/ul/li[3]/div").click()
    except:
        filmweb_ads()
        driver.get("https://filmweb.pl/login")
        driver.find_element_by_xpath("//*[@id=\"site\"]/div[2]/div/div/div[1]/div/div/ul/li[3]/div").click()
    driver.find_element_by_name("j_username").send_keys(username)
    driver.find_element_by_name("j_password").send_keys(password)
    time.sleep(5)
    driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div/form/div[2]/ul/li[1]/button").click()
    time.sleep(5)
    driver.get("https://filmweb.pl/settings")
    time.sleep(5)
    if driver.current_url != "https://www.filmweb.pl/settings":
        console.log("[red]Login failed. Probably because of captcha. Insert session and token cookie into settings.cfg manually.[/red]")
        return(False)
    else:
        parse_config()
        fetched_session = driver.get_cookie("_fwuser_sessionId")
        fetched_token = driver.get_cookie("_fwuser_token")
        settings.set("settings", "session", str(fetched_session))
        settings.set("settings", "token", str(fetched_token))
        settings.write
        parse_config()
        console.log("[green]Logged in and saved new cookies to settings.cfg[/green]")

def filmweb_ads():
    try:
        driver.find_element_by_id("didomi-notice-agree-button").click()
    except:
        driver.find_element_by_class_name("ws__skipButton").click()
    return

def rating_sanitizer(rating):
    if rating == "":
        return(0)
    rating = rating[0]
    if rating == "0":
        return("10")
    return(rating)

def txt_to_filmweb():
    movies = open(userVariables["movies"], "r")
    for title in track(movies):
        rating = "".join(re.findall(r"/\d\d\/|\d[,.]\d\/|\d[,.]\d|\d\/", title))
        rating = rating_sanitizer(rating)
        title = re.sub("\d\d\/10|\d[,.]\d\/10|\d[,.]\d|\d\/..", "", title)
        title = re.sub("\s+$", "", title)
        title = title.replace(" ", "+")

        if rating == 0:
            console.log("Rating not provided for title: " + title, style="bold orange")
            continue
        
        console.log("Fetched title: " + title + " and rating: " + rating, style="bold green")
        driver.get("https://filmweb.pl/search?q=" + title)
        url = driver.current_url
        if "type=user" in url:
            print("Title " + title + " not found in Filmweb database")
            continue
        
        try:
            driver.find_element_by_class_name("filmPreview__link").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[1]").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[2]/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/a[" + rating + "]").click()
        except NoSuchElementException:
            print("Title " + title + " not found in Filmweb database")
            continue
        except:
            filmweb_ads()
            driver.find_element_by_class_name("filmPreview__link").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[1]").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[2]/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/a[" + rating + "]").click()

def filmweb_export(username):
    done = False
    titles = []
    years = []
    ratings = []
    const = []
    p = 1
    with console.status("[bold green]Fetching ratings...") as status:
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
            const.append("error")
        i += 1

    for i in range(0, len(const)):
        fetchedRatings.append(dict({"Const": str(const[i]),"Title": titles[i], "Year": years[i], "Your Rating": ratings[i]}))
    
    with open("export.csv", "w", newline="") as imdbCSV:
        fieldnames = ["Position", "Const", "Created", "Modified", "Description", "Title", "URL", "Title Type", "IMDb Rating", "Runtime (mins)", "Year", "Genres", "Num Votes", "Release Date", "Directors", "Your Rating", "Date Rated"]
        writer = csv.DictWriter(imdbCSV, fieldnames=fieldnames)
        writer.writeheader()
        for fetchedRating in fetchedRatings:
            writer.writerow(fetchedRating)
