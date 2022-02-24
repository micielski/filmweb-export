from bs4 import BeautifulSoup
import requests
import os
import sys
import time
import json
from colorama import Fore, Style

from filmweb.base import Movie, current_date

fw_cookies = {
    "_fwuser_logged": "1",
    "_fwuser_token": None,
    "_fwuser_sessionId": None
}


def get_username():
    r = requests.get("https://filmweb.pl/settings", cookies=fw_cookies)
    soup = BeautifulSoup(r.text, "lxml")
    return soup.find(class_="userAvatar__image").attrs["alt"]


def scrape(page, username, title_type):
    r = requests.get(f"https://filmweb.pl/user/{username}/{title_type}?page={page}", cookies=fw_cookies)
    if "emptyContent" in r.text:
        if type == "serials":
            print(f"Export finished in export-{current_date}.csv")
        return True

    soup = BeautifulSoup(r.text, "lxml")
    titles_amount = soup.find_all(class_="myVoteBox__mainBox")
    print(f"Scraping {len(titles_amount)} {title_type} from page {page}")
    scripts = soup.find("span", class_="dataSource").extract() if title_type != "wantToSee" else None
    for _ in titles_amount:
        vote_box = soup.find(class_="myVoteBox__mainBox").extract()
        title = vote_box.find(class_="filmPreview__title").text
        orig_title = vote_box.find(class_="filmPreview__originalTitle")
        translated = False if orig_title is None else True
        year = vote_box.find(class_="filmPreview__year").text
        rating = scripts.find("script").extract().text if title_type != "wantToSee" else None
        rating = json.loads(rating)["r"] if title_type != "wantToSee" else None
        Movie(title, orig_title, year, rating, translated, title_type)


def set_cookies(token, session):
    fw_cookies["_fwuser_token"] = token
    fw_cookies["_fwuser_sessionId"] = session
    if not fw_cookies["_fwuser_token"]:
        print(fw_cookies["_fwuser_token"])
        print(f"{Fore.RED}No cookie \"_fwuser_token\" was provided{Style.RESET_ALL}")
        fw_cookies["_fwuser_token"] = input("_fwuser_token: ")
    if not fw_cookies["_fwuser_sessionId"]:
        print(f"{Fore.RED}No cookie \"_fwuser_sessionId\" was provided{Style.RESET_ALL}")
        fw_cookies["_fwuser_sessionId"] = input("_fwuser_sessionId: ")
    r = requests.get("https://filmweb.pl/settings", cookies=fw_cookies)
    if "Twój adres IP" in r.text:
        print("Valid cookies")
        return True
    else:
        print(f"{Fore.RED}Invalid cookies")
        return False


def login(chrome, firefox):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    if chrome or not chrome and not firefox:
        options = ChromeOptions()
        options.add_argument("headless")
        options.add_argument("window-size=800x600")
        driver = webdriver.Chrome(options=options)
    else:
        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(15)
    driver.get("https://filmweb.pl/login")
    try:  # because of chrome's weirdness
        driver.find_element(By.ID, "didomi-notice-agree-button").click()
    except NoSuchElementException:
        pass
    driver.find_elements(By.CLASS_NAME, "authButton__text")[1].click()
    driver.find_element(By.NAME, "j_username").send_keys(input("Username: "))
    os.system("stty -echo")
    driver.find_element(By.NAME, "j_password").send_keys(input("Password: "))
    driver.find_element(By.CLASS_NAME, "popupForm__button").click()
    time.sleep(5)
    os.system("stty echo")
    print("\n")
    driver.get("https://filmweb.pl/settings")
    time.sleep(5)
    try:
        fw_cookies["_fwuser_sessionId"] = driver.get_cookie("_fwuser_sessionId")["value"]
        fw_cookies["_fwuser_token"] = driver.get_cookie("_fwuser_token")["value"]
        return
    except TypeError:
        print("Either wrong password, or captcha popped up. Try typing in cookies manually")
        sys.exit(1)
