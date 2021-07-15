from selenium import webdriver
import configparser
import re
import time

settings = configparser.ConfigParser()
settings.read("settings.cfg")

chromedriver = settings.get("settings", "chromedriver")
movies = settings.get("settings", "list")
username = settings.get("settings", "username")
password = settings.get("settings", "password")
timeout = settings.get("settings", "timeout")
loginTimeout = int(settings.get("settings", "login_timeout"))

driver = webdriver.Chrome(chromedriver)
driver.implicitly_wait(timeout)

movies = open(movies, "r")

driver.get("https://www.filmweb.pl/")
driver.find_element_by_id("didomi-notice-agree-button").click()

def filmweb_login():
    driver.get("https://www.filmweb.pl/login")
    driver.find_element_by_xpath("//*[@id=\"site\"]/div[2]/div/div/div[1]/div/div/ul/li[3]/div").click()
    driver.find_element_by_name("j_username").send_keys(username)
    driver.find_element_by_name("j_password").send_keys(password)
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

filmweb_login()
txt_to_filmweb()

  