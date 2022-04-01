import json
import math
import os
import time
import sys
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style
from requests.adapters import HTTPAdapter, Retry
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from filmweb.base import Movie, current_date

fw_cookies = {
    "_fwuser_logged": "1",
    "_fwuser_token": None,
    "_fwuser_sessionId": None,
    "JWT": None
}


class FilmwebPage:
    def __init__(self, username: str, title_type: str, page: int):
        assert page >= 1, "Page should not be lower than 1"
        self.username = username
        self.title_type = title_type
        self.page = page
        self.api_type = "film" if title_type == "films" else "serial"
        self.page_source = self.get_page_source()
        self.soup = self.get_soup()
        self.titles_amount = self.get_titles_amount()

        if "emptyContent" in self.page_source.text:
            if type == "serials":
                print(f"Export finished in export-{current_date}.csv")
            return

        for box in self.titles_amount:
            if self.title_type != "wantToSee":
                title_id = self.get_title_id()
                r_api = requests.get(f"https://api.filmweb.pl/v1/logged/vote/{self.api_type}/{title_id}/details",
                                     cookies=fw_cookies)
                if "400 Invalid token" in r_api.text:
                    print("Token JWT invalidated. Please run me again with a new token")
                    sys.exit(1)
                json_api = json.loads(r_api.text)
                rating = int(json_api["rate"])
            else:
                rating = None
            title = self.get_title(box)
            orig_title = self.get_orig_title(box)
            year = int(self.get_year(box))
            Movie(title, orig_title, year, rating, self.title_type)

    @staticmethod
    def get_year(box):
        try:
            return box.find(class_="preview__year").text
        except AttributeError:
            return box.find(class_="filmPreview__year").text

    @staticmethod
    def get_orig_title(box):
        try:
            orig_title = box.find(class_="preview__originalTitle")
            return orig_title.text if orig_title else None
        except AttributeError:
            orig_title = box.find(class_="filmPreview__originalTitle")
            return orig_title.text if orig_title else None

    @staticmethod
    def get_title(box):
        try:
            title = box.find(class_="preview__link")
            return title.text if title else None
        except AttributeError:
            title = box.find(class_="filmPreview__title")
            return title.text if title else None

    def get_title_id(self):
        return self.soup.find(class_="ribbon").extract()\
               .get_attribute_list("data-id")[0]

    def get_titles_amount(self):
        return self.soup.find_all(class_="myVoteBox__mainBox")

    def get_page_source(self):
        request = requests.get(f"https://filmweb.pl/user/{self.username}/{self.title_type}?page={self.page}",
                               cookies=fw_cookies)
        return request

    def get_soup(self):
        return BeautifulSoup(self.page_source.text, "lxml")


def get_username():
    page_source = requests.get("https://filmweb.pl/settings", cookies=fw_cookies).text
    soup = BeautifulSoup(page_source, "lxml")
    return soup.find(class_="userAvatar__image").attrs["alt"]


def get_pages_count(username):
    page_source = requests.get(f"https://filmweb.pl/user/{username}").text
    soup = BeautifulSoup(page_source, "lxml")
    extracted_data = soup.find(class_="voteStatsBox VoteStatsBox")
    f_pages = math.ceil(
        int(extracted_data.get_attribute_list("data-filmratedcount")[0])/25)
    s_pages = math.ceil(
        int(extracted_data.get_attribute_list("data-serialratedcount")[0])/25)
    w_pages = math.ceil(
        int(extracted_data.get_attribute_list("data-filmw2scount")[0])/25)
    return f_pages, s_pages, w_pages


def scrape_multithreaded(username, title_type, page):
    session = requests.Session()
    retries = Retry(total=10, backoff_factor=0.2)
    session.mount("https://", HTTPAdapter(max_retries=retries))
    FilmwebPage(username, title_type, page)


def set_cookies(token, session, jwt):
    fw_cookies["_fwuser_token"] = token
    fw_cookies["_fwuser_sessionId"] = session
    fw_cookies["JWT"] = jwt
    if not fw_cookies["_fwuser_token"]:
        print(f"{Fore.YELLOW}No cookie \"_fwuser_token\" was provided{Style.RESET_ALL}")
        fw_cookies["_fwuser_token"] = input("_fwuser_token: ")
    if not fw_cookies["_fwuser_sessionId"]:
        print(
            f"{Fore.YELLOW}No cookie \"_fwuser_sessionId\" was provided{Style.RESET_ALL}")
        fw_cookies["_fwuser_sessionId"] = input("_fwuser_sessionId: ")
    if not fw_cookies["JWT"]:
        print(f"{Fore.YELLOW}No cookie \"JWT\" was provided{Style.RESET_ALL}")
        fw_cookies["JWT"] = input("JWT: ")
    page_source = requests.get("https://filmweb.pl/settings", cookies=fw_cookies).text
    if "Twój adres IP" not in page_source:
        print(f"{Fore.RED}Invalid cookies")
        return False
    print("Valid cookies")
    return True


def login(chrome, firefox):
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
        fw_cookies["_fwuser_sessionId"] = driver.get_cookie("_fwuser_sessionId")[
            "value"]
        fw_cookies["_fwuser_token"] = driver.get_cookie("_fwuser_token")[
            "value"]
        fw_cookies["JWT"] = driver.get_cookie("JWT")["value"]
        return
    except TypeError:
        print("Either wrong password, or captcha popped up. Try typing in cookies manually")
        sys.exit(1)
