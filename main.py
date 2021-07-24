from selenium import webdriver
from bs4 import BeautifulSoup
import configparser
import re
import time

settings = configparser.ConfigParser()
settings.read("settings.cfg")

userVariables = {}
for i in ["chromedriver", "movies", "username", "password", "timeout"]:
    userVariables[i] = settings.get("settings", i)

driver = webdriver.Chrome(userVariables["chromedriver"])
driver.implicitly_wait(userVariables["timeout"])

movies = open(userVariables["movies"], "r")

driver.get("https://www.filmweb.pl/")
driver.find_element_by_id("didomi-notice-agree-button").click()


def filmweb_login():
    driver.get("https://www.filmweb.pl/login")
    driver.find_element_by_xpath("//*[@id=\"site\"]/div[2]/div/div/div[1]/div/div/ul/li[3]/div").click()
    driver.find_element_by_name("j_username").send_keys(userVariables["username"])
    driver.find_element_by_name("j_password").send_keys(userVariables["password"])
    time.sleep(loginTimeout/2)
    driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div/form/div[2]/ul/li[1]/button").click()
    time.sleep(loginTimeout/2)


def txt_to_filmweb():
    for title in movies:
        rating = "".join(re.findall(r"(\d+)/", title))
        title = re.sub("[0-9]+/\d\d$", "", title)
        title = re.sub("\s+$", "", title)
        title = title.replace(" ", "+")
        driver.get("https://www.filmweb.pl/search?q=" + title)
        driver.find_element_by_class_name("filmPreview__link").click()
        driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[1]").click()
        driver.find_element_by_xpath("//*[@id=\"site\"]/div[3]/div[3]/div/div[2]/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/a[" + rating + "]").click()


def filmweb_Import():
    driver.get("https://www.filmweb.pl/user/" + userVariables["username"] + "/films")
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    
    ratings = soup.find_all(class_="userRate__rate")

    for rating in ratings:
        print(rating.text)

# filmweb_login()
# txt_to_filmweb()

filmweb_Import()