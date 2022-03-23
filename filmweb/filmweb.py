from bs4 import BeautifulSoup
from colorama import Fore, Style
from requests.adapters import HTTPAdapter, Retry
import json
import math
import os
import requests
import sys
import time

from filmweb.base import Movie, current_date

fw_cookies = {
    "_fwuser_logged": "1",
    "_fwuser_token": None,
    "_fwuser_sessionId": None,
    "JWT": None
}


def get_username():
    r = requests.get("https://filmweb.pl/settings", cookies=fw_cookies)
    soup = BeautifulSoup(r.text, "lxml")
    return soup.find(class_="userAvatar__image").attrs["alt"]


def get_pages_count(username):
    r = requests.get(f"https://filmweb.pl/user/{username}")
    soup = BeautifulSoup(r.text, "lxml")
    extracted_data = soup.find(class_="voteStatsBox VoteStatsBox")
    f_pages = math.ceil(int(extracted_data.get_attribute_list("data-filmratedcount")[0])/25)
    s_pages = math.ceil(int(extracted_data.get_attribute_list("data-serialratedcount")[0])/25)
    w_pages = math.ceil(int(extracted_data.get_attribute_list("data-filmw2scount")[0])/25)
    return f_pages, s_pages, w_pages


def scrape_multithreaded(username, title_type, page):
    s = requests.Session()
    retries = Retry(total=10, backoff_factor=0.2)
    s.mount("https://", HTTPAdapter(max_retries=retries))
    scrape(username, title_type, page)


def scrape(username, title_type, page):
    r = requests.get(f"https://filmweb.pl/user/{username}/{title_type}?page={page}", cookies=fw_cookies)
    if "emptyContent" in r.text:
        if type == "serials":
            print(f"Export finished in export-{current_date}.csv")
        return True

    soup = BeautifulSoup(r.text, "lxml")
    titles_amount = soup.find_all(class_="myVoteBox__mainBox")
    for _ in titles_amount:
        if title_type != "wantToSee":
            title_id = soup.find(class_="ribbon").extract().get_attribute_list("data-id")[0]
            api_type = "film" if title_type == "films" else "serials"
            r_api = requests.get(f"https://api.filmweb.pl/v1/logged/vote/{api_type}/{title_id}/details", cookies=fw_cookies)
            json_api = json.loads(r_api.text)
            rating = json_api["rate"]
        else:
            rating = None

        vote_box = soup.find(class_="myVoteBox__mainBox").extract()
        title = vote_box.find(class_="filmPreview__title")
        title = title.text if title != None else None
        orig_title = vote_box.find(class_="filmPreview__originalTitle")
        orig_title = orig_title.text if orig_title is not None else None
        translated = False if orig_title is None else True
        year = vote_box.find(class_="filmPreview__year").text
        Movie(title, orig_title, year, rating, translated, title_type)


def set_cookies(token, session, jwt):
    fw_cookies["_fwuser_token"] = token
    fw_cookies["_fwuser_sessionId"] = session
    fw_cookies["JWT"] = jwt
    if not fw_cookies["_fwuser_token"]:
        print(f"{Fore.RED}No cookie \"_fwuser_token\" was provided{Style.RESET_ALL}")
        fw_cookies["_fwuser_token"] = input("_fwuser_token: ")
    if not fw_cookies["_fwuser_sessionId"]:
        print(f"{Fore.RED}No cookie \"_fwuser_sessionId\" was provided{Style.RESET_ALL}")
        fw_cookies["_fwuser_sessionId"] = input("_fwuser_sessionId: ")
    if not fw_cookies["JWT"]:
        print(f"{Fore.RED}No cookie \"JWT\" was provided{Style.RESET_ALL}")
        fw_cookies["JWT"] = input("JWT: ")
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
    if chrome or not chrome and not firefox and not os.environ.get("DOCKER"):
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
        fw_cookies["JWT"] = driver.get_cookie("JWT")["value"]
        return
    except TypeError:
        print("Either wrong password, or captcha popped up. Try typing in cookies manually")
        sys.exit(1)

