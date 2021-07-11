from selenium import webdriver
import re
import time

list = "list-directory"
chromedriver = "chromedriver-directory"

f = open(list, "r")

browser = webdriver.Chrome(chromedriver)
browser.set_window_size(1920, 1080)
browser.get("https://www.filmweb.pl/")
browser.find_element_by_xpath("//*[@id=\"didomi-notice-agree-button\"]").click()

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
    time.sleep(1)
