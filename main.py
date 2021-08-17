from os import name
from bs4.element import Tag
from selenium import webdriver
from bs4 import BeautifulSoup
import configparser
import re
import time
import csv

userVariables = {}
settings = configparser.ConfigParser()

def parseConfig():
    settings.read("settings.cfg")

    for i in ["chromedriver", "movies", "username", "password", "timeout", "token", "session"]:
        userVariables[i] = settings.get("settings", i)

parseConfig()
driver = webdriver.Chrome(userVariables["chromedriver"])

def setCookies():
    cookieLogged = {"name": "_fwuser_logged", "value": "1"}
    cookieToken = {"name": "_fwuser_token", "value": userVariables["token"] }
    cookieSession = {"name": "_fwuser_sessionId", "value": userVariables["session"]}
    driver.add_cookie(cookieLogged)
    driver.add_cookie(cookieToken)
    driver.add_cookie(cookieSession)
    driver.get("https://filmweb.pl/settings")
    if driver.current_url != "https://www.filmweb.pl/settings":
        print("token and session invalid, performing a logging in action")
    else:
        print("we're in!")

def filmwebLogin():
    driver.get("https://filmweb.pl/login")
    driver.find_element_by_xpath("//*[@id=\"site\"]/div[2]/div/div/div[1]/div/div/ul/li[3]/div").click()
    driver.find_element_by_name("j_username").send_keys(userVariables["username"])
    driver.find_element_by_name("j_password").send_keys(userVariables["password"])
    time.sleep(int(userVariables["timeout"])/2)
    driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div/form/div[2]/ul/li[1]/button").click()
    time.sleep(int(userVariables["timeout"])/2)
    fetchedSession = driver.get_cookie("_fwuser_sessionId")
    fetchedToken = driver.get_cookie("_fwuser_token")
    settings.set("settings", "session", str(fetchedSession))
    settings.set("settings", "token", str(fetchedToken))
    settings.write("settings.cfg")
    parseConfig()

def filmwebAds():
    try:
        driver.find_element_by_id("didomi-notice-agree-button").click()
    except:
        driver.find_element_by_class_name("ws__skipButton").click()

    return(True)

def txtToFilmweb():
    movies = open(userVariables["movies"], "r")
    for title in movies:
        rating = "".join(re.findall(r"\d\/|\d[,.]\d\/|\d[,.]\d", title))
        rating = rating.strip("/")
        #rating = "".join(re.findall(r"(\d+)/", title))
        title = re.sub("[0-9]+/\d\d$", "", title)
        title = re.sub("\s+$", "", title)
        title = title.replace(" ", "+")
        
        print("Fetched title: " + title + " and rating: " + rating)
        driver.get("https://filmweb.pl/search?q=" + title)
        
        try:
            driver.find_element_by_class_name("filmPreview__link").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[1]").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[2]/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/a[" + rating + "]").click()
        except:
            filmwebAds()
            driver.find_element_by_class_name("filmPreview__link").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[1]").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[2]/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/a[" + rating + "]").click()

def filmwebExport():

    driver.get("https://filmweb.pl/user/" + userVariables["username"] + "/films")
    
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    
    actors = soup.find_all(class_="myVoteBox__rightCol")
    actors2 = soup.find_all(class_="barFilter__desc")

    for actor in actors:
        actor.decompose()

    for actor2 in actors2:
        actor2.decompose()

    titles = soup.find_all(class_="filmPreview__title")

    links = []
    for link in soup.find_all(class_="filmPreview__link"):
        links.append(link.get('href'))

    print(links[0])

    years = soup.find_all(class_="filmPreview__year")
    ratings = soup.find_all(class_="userRate__rate")
    directors = soup.find_all("span", itemprop="name")
    titlesAmount = len(titles)
    fetchedRatings = []

    i = 0
    while i <= titlesAmount:
        driver.get("https://imdb.com/search/title/")
        print("Searching for: " + titles[i].text)
        driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[3]/form/div/div[1]/div[2]/input").send_keys(titles[i].text)
        driver.find_element_by_name("release_date-min").send_keys(years[i].text)
        driver.find_element_by_name("release_date-max").send_keys(years[i].text)
        time.sleep(5)
        driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div[3]/form/div/p[3]/button").click()
        try:
            driver.find_element_by_class_name("loadlate").click()
        except:
            print(titles[i].text + " Not Found. Skipping")
        time.sleep(5)
        i += 1



    for i in range(0, titlesAmount):
        fetchedRatings.append(dict({"Title": titles[i].text, "Directors": directors[i].text, "Year": years[i].text, "Your Rating": ratings[i].text}))
    
    print(fetchedRatings)
    '''
    with open("export.csv", "w", newline="") as imdbCSV:
        fieldnames = ["Position", "Const", "Created", "Modified", "Description", "Title", "URL", "Title Type", "IMDb Rating", "Runtime (mins)", "Year", "Genres", "Num Votes", "Release Date", "Directors", "Your Rating", "Date Rated"]
        writer = csv.DictWriter(imdbCSV, fieldnames=fieldnames)
        writer.writeheader()
        for fetchedRating in fetchedRatings:
            writer.writerow(fetchedRating)
    '''




#driver = webdriver.Firefox(userVariables["chromedriver"])
driver.implicitly_wait(userVariables["timeout"])
driver.get("https://filmweb.pl/")

#filmwebLogin()
#setCookies()
#filmwebExport()
filmwebAds()
txtToFilmweb()
