from bs4.element import Tag
from selenium import webdriver
from bs4 import BeautifulSoup
import configparser
import re
import time
import csv

userVariables = {}

def parseConfig():
    settings = configparser.ConfigParser()
    settings.read("settings.cfg")

    for i in ["chromedriver", "movies", "username", "password", "timeout", "token", "session"]:
        userVariables[i] = settings.get("settings", i)

def setCookies():
    cookieLogged = {"name": "_fwuser_logged", "value": "1"}
    cookieToken = {"name": "_fwuser_token", "value": userVariables["token"] }
    cookieSession = {"name": "_fwuser_sessionId", "value": userVariables["session"]}
    driver.add_cookie(cookieLogged)
    driver.add_cookie(cookieToken)
    driver.add_cookie(cookieSession)

def filmweb_login():
    driver.get("https://www.filmweb.pl/login")
    driver.find_element_by_xpath("//*[@id=\"site\"]/div[2]/div/div/div[1]/div/div/ul/li[3]/div").click()
    driver.find_element_by_name("j_username").send_keys(userVariables["username"])
    driver.find_element_by_name("j_password").send_keys(userVariables["password"])
    time.sleep(int(userVariables["timeout"])/2)
    driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div/form/div[2]/ul/li[1]/button").click()
    time.sleep(int(userVariables["timeout"])/2)


def txt_to_filmweb():
    movies = open(userVariables["movies"], "r")
    for title in movies:
        rating = "".join(re.findall(r"(\d+)/", title))
        title = re.sub("[0-9]+/\d\d$", "", title)
        title = re.sub("\s+$", "", title)
        title = title.replace(" ", "+")
        driver.get("https://www.filmweb.pl/search?q=" + title)
        driver.find_element_by_class_name("filmPreview__link").click()
        driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[1]").click()
        driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[2]/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/a[" + rating + "]").click()


def filmweb_Export():

    driver.get("https://www.filmweb.pl/user/" + userVariables["username"] + "/films")
    
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    
    actors = soup.find_all(class_="myVoteBox__rightCol")
    actors2 = soup.find_all(class_="barFilter__desc")
    #print(actors)

    for actor in actors:
        actor.decompose()

    for actor2 in actors2:
        actor2.decompose()

    print(soup.prettify)
    titles = soup.find_all(class_="filmPreview__title")
    years = soup.find_all(class_="filmPreview__year")
    ratings = soup.find_all(class_="userRate__rate")
    directors = soup.find_all("span", itemprop="name")
    titlesAmount = len(titles)
    fetchedRatings = []

    for i in range(0, titlesAmount):
        fetchedRatings.append(dict({"title": titles[i].text, "director": directors[i].text, "year": years[i].text, "rating": ratings[i].text}))
    
    print(fetchedRatings)

#filmweb_login()
#txt_to_filmweb()


parseConfig()

driver = webdriver.Chrome(userVariables["chromedriver"])
driver.implicitly_wait(userVariables["timeout"])
driver.get("https://www.filmweb.pl/")

setCookies()
filmweb_Export()
