from os import name
import configparser
import re
import time
import csv
#from bs4.element import Tag
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

userVariables = {}
settings = configparser.ConfigParser()

def parse_config():
    settings.read("settings.cfg")

    for i in ["chromedriver", "movies", "username", "password", "timeout", "token", "session"]:
        userVariables[i] = settings.get("settings", i)

parse_config()
driver = webdriver.Chrome(userVariables["chromedriver"])

def set_cookies():
    cookie_logged = {"name": "_fwuser_logged", "value": "1"}
    cookie_token = {"name": "_fwuser_token", "value": userVariables["token"] }
    cookie_session = {"name": "_fwuser_sessionId", "value": userVariables["session"]}
    driver.add_cookie(cookie_logged)
    driver.add_cookie(cookie_token)
    driver.add_cookie(cookie_session)
    driver.get("https://filmweb.pl/settings")
    if driver.current_url != "https://www.filmweb.pl/settings":
        print("token and session invalid, performing a logging in action")
    else:
        print("we're in!")

def filmweb_login():
    driver.get("https://filmweb.pl/login")
    driver.find_element_by_xpath("//*[@id=\"site\"]/div[2]/div/div/div[1]/div/div/ul/li[3]/div").click()
    driver.find_element_by_name("j_username").send_keys(userVariables["username"])
    driver.find_element_by_name("j_password").send_keys(userVariables["password"])
    time.sleep(int(userVariables["timeout"])/2)
    driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div/form/div[2]/ul/li[1]/button").click()
    time.sleep(int(userVariables["timeout"])/2)
    fetched_session = driver.get_cookie("_fwuser_sessionId")
    fetched_token = driver.get_cookie("_fwuser_token")
    settings.set("settings", "session", str(fetched_session))
    settings.set("settings", "token", str(fetched_token))
    settings.write("settings.cfg")
    parse_config()

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
    for title in movies:
        rating = "".join(re.findall(r"/\d\d\/|\d[,.]\d\/|\d[,.]\d|\d\/", title))
        rating = rating_sanitizer(rating)
        title = re.sub("\d\d\/10|\d[,.]\d\/10|\d[,.]\d|\d\/..", "", title)
        title = re.sub("\s+$", "", title)
        title = title.replace(" ", "+")

        if rating == 0:
            print("Rating not provided for title: " + title)
            continue
        
        print("Fetched title: " + title + " and rating: " + rating)
        driver.get("https://filmweb.pl/search?q=" + title)
        url = driver.current_url
        if "type=user" in url:
            print("Title " + title + "not found in Filmweb database 1")
            continue
        
        try:
            driver.find_element_by_class_name("filmPreview__link").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[1]").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[2]/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/a[" + rating + "]").click()
        except NoSuchElementException as exception:
            print("Title " + title + "not found in Filmweb database 2")
            continue
        except:
            filmweb_ads()
            driver.find_element_by_class_name("filmPreview__link").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[1]").click()
            driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[2]/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/a[" + rating + "]").click()

def filmweb_export():

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
    titles_amount = len(titles)
    fetchedRatings = []

    i = 0
    while i <= titles_amount:
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



    for i in range(0, titles_amount):
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

#filmweb_login()
#set_cookies()
#filmweb_export()
filmweb_ads()
txt_to_filmweb()
