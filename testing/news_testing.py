from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import pandas as pd
import random
import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from datetime import date
from datetime import datetime
from dateutil import parser

def initialize_browser_markets():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    #options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    return browser

def get_readable_date(iso_date_str):
    try:
        date_obj = datetime.strptime(iso_date_str, "%Y-%m-%d")
        # Reformat the datetime object to "February 17, 2024" format
        readable_date = date_obj.strftime("%B %d, %Y")
        return readable_date
    except ValueError:
        return iso_date_str

def get_sortable_date(date_str):
    if date_str in ["N/A", ""]:
        return (1, datetime.min)  # Sort "N/A" or empty dates to the end
    try:
        parsed_date = parser.parse(date_str)
        return (0, parsed_date)
    except ValueError:
        return (1, datetime.min)  # Sort unparsable dates to the end

def scroll_and_scrape_nytimes(browser):
    base_url = "https://www.nytimes.com/ca/section/world/asia"
    all_news = []
    browser.get(base_url)
    time.sleep(5)

    for _ in range(7):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        news_containers = browser.find_elements(By.CSS_SELECTOR, "li.css-18yolpw")
        for container in news_containers:
            news_info = {
                "URL": "N/A",
                "Image": "N/A",
                "Title": "N/A",
                "Description": "N/A",
                "Date": "N/A"
            }

            # Extract URL and Title
            try:
                url_element = container.find_element(By.CSS_SELECTOR, "a")
                news_info["URL"] = url_element.get_attribute('href')
                title_element = container.find_element(By.CSS_SELECTOR, "a h3")
                news_info["Title"] = title_element.text.strip()
            except NoSuchElementException:
                print("URL or Title element not found.")

            # Extract Image
            try:
                image_element = container.find_element(By.CSS_SELECTOR, "div.css-79elbk img")
                news_info["Image"] = image_element.get_attribute('src')
            except NoSuchElementException:
                print("Image element not found.")

            # Extract Description
            try:
                description_element = container.find_element(By.CSS_SELECTOR, "p")
                news_info["Description"] = description_element.text.strip()
            except NoSuchElementException:
                print("Description element not found.")

            # Extract Date
            try:
                date_element = container.find_element(By.CSS_SELECTOR, "div.css-agsgss span")
                news_info["Date"] = date_element.text.strip()
            except NoSuchElementException:
                print("Date element not found.")

            all_news.append(news_info)

    all_news = sorted(all_news, key=lambda x: get_sortable_date(x['Date']), reverse=True)
    return all_news

def scroll_and_scrape_fx(browser):
    base_url = "https://www.fx-markets.com/regions/asia"
    all_news = []
    browser.get(base_url)
    time.sleep(5)

    scroll_count = 0
    while scroll_count <= 2:
        news_containers = browser.find_elements(By.CSS_SELECTOR, "article")
        for container in news_containers:
            news_info = {
                "URL": "N/A",
                "Image": "N/A",
                "Title": "N/A",
                "Description": "N/A",
                "Date": "N/A"
            }

            # Extract URL and Title
            try:
                title_element = container.find_element(By.CSS_SELECTOR, "h5.article-title a")
                news_info["URL"] = title_element.get_attribute('href')
                news_info["Title"] = title_element.text.strip()
            except NoSuchElementException:
                print("URL or Title element not found.")

            # Extract Image
            try:
                image_element = container.find_element(By.CSS_SELECTOR, "div.image-text-group-a img")
                news_info["Image"] = image_element.get_attribute('src')
            except NoSuchElementException:
                print("Image element not found.")

            # Extract Description
            try:
                description_element = container.find_element(By.CSS_SELECTOR, "p")
                news_info["Description"] = description_element.text.strip()
            except NoSuchElementException:
                print("Description element not found.")

            # Extract Date
            try:
                date_element = container.find_element(By.CSS_SELECTOR, "li.publish-date time")
                iso_date_str = date_element.get_attribute("datetime")
                if iso_date_str:
                    readable_date = get_readable_date(iso_date_str)  # Converts ISO to readable format
                    news_info["ReadableDate"] = readable_date  # Store readable format
                    news_info["ISODate"] = iso_date_str  # Keep ISO format for sorting
            except NoSuchElementException:
                print("Date element not found.")

            all_news.append(news_info)

        try:
            next_button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[@class='next ']/a[@rel='next']"))
            )
            browser.execute_script("arguments[0].click();", next_button)
            time.sleep(random.uniform(2, 4))
            scroll_count += 1
        except TimeoutException:
            break

    if len(all_news) > 4:
        all_news = all_news[4:]

    all_news = sorted(all_news, key=lambda x: get_sortable_date(x['ISODate']), reverse=True)
    return all_news



def moves_to_excel(profiles, filename="Market_News.xlsx"):
    df = pd.DataFrame(profiles)
    df.to_excel(filename, index=False)
    print(f"Data exported to {filename}")

# Example of how to run
browser = initialize_browser_markets()
nytimes_news = scroll_and_scrape_nytimes(browser)
fx_news = scroll_and_scrape_fx(browser)
combined_news = nytimes_news + fx_news
moves_to_excel(combined_news, filename="Combined_Market_News.xlsx")
