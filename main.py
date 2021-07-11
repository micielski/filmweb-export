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

print(chromedriver)
print(movies)
print(username)
print(password)

f = open(movies, "r")
print(f)

browser = webdriver.Chrome(chromedriver)
browser.set_window_size(1920, 1080)
browser.get("https://www.filmweb.pl/")
browser.find_element_by_xpath("//*[@id=\"didomi-notice-agree-button\"]").click()
browser.find_element_by_xpath("//*[@id=\"main-header_login-link\"]").click()
browser.find_element_by_xpath("//*[@id=\"site\"]/div[2]/div/div/div[1]/div/div/ul/li[3]/div").click()
browser.find_element_by_name("j_username").send_keys(username)
browser.find_element_by_name("j_password").send_keys(password)


'''
for x in f:
    ocena = "".join(re.findall(r"(\d+)/", x))
    x = re.sub("[0-9]+/\d\d$", "", x)
    x = re.sub("\s+$", "", x)
    x = x.replace(" ", "+")
    browser.get("https://www.filmweb.pl/search?q=" + x)
    browser.find_element_by_class_name("filmPreview__link").click()
    time.sleep(5)
    browser.find_element_by_xpath("/html/body/div[4]/div[3]/div[2]/div/div[3]/section/div/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/a[" + ocena + "]").click()
    print("Done executing")
    time.sleep(1)'''
