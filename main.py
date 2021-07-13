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

movies = open(movies, "r")

driver = webdriver.Chrome(chromedriver)
driver.set_window_size(1920, 1080)
driver.get("https://www.filmweb.pl/")
driver.implicitly_wait(10)
driver.find_element_by_xpath("//*[@id=\"didomi-notice-agree-button\"]").click()
driver.find_element_by_xpath("//*[@id=\"main-header_login-link\"]").click()
driver.find_element_by_xpath("//*[@id=\"site\"]/div[2]/div/div/div[1]/div/div/ul/li[3]/div").click()
driver.find_element_by_name("j_username").send_keys(username)
driver.find_element_by_name("j_password").send_keys(password)
time.sleep(5)
driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div/form/div[2]/ul/li[1]/button").click()
time.sleep(5)

for title in movies:
    rating = "".join(re.findall(r"(\d+)/", title))
    title = re.sub("[0-9]+/\d\d$", "", title)
    title = re.sub("\s+$", "", title)
    title = title.replace(" ", "+")
    driver.get("https://www.filmweb.pl/search?q=" + title)
    driver.find_element_by_class_name("filmPreview__link").click()
    driver.find_element_by_xpath("/html/body/div[3]/div[3]/div[2]/div/div[3]/section/div/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/a["+ rating +"]").click()
