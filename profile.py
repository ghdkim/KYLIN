from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import time
import random
import os

def initialize_browser():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    return browser

def scroll_page(browser, role, bank, department, region):
    # Scrolls through the Google search results page and loads more results
    base_url = f"https://www.google.com/search?q=site:linkedin.com/in/+AND+intitle:{role}+{department}+{bank}+{region}+AND+'Investment+Banking'"
    browser.get(base_url)
    time.sleep(5)

    try:
        last_height = browser.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        while scroll_count < 1:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.5, 3.5))

            # Check for the "More search results" button and click if present
            try:
                more_results_button = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.T7sFge.sW9g3e.VknLRd"))
                )
                browser.execute_script("arguments[0].click();", more_results_button)
                time.sleep(random.uniform(1.5, 3.5))
            except TimeoutException:
                print("No more 'More search results' button found.")
                break

            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_count += 1

    except Exception as e:
        print(f"Error during scrolling: {e}")

def scrape_multiple_profiles(browser, role, department, bank, region):
    scroll_page(browser, role, department, bank, region)
    all_profiles = []

    try:
        # Locate all profile containers on the page
        profile_containers = browser.find_elements(By.CSS_SELECTOR, "div.MjjYud")

        for container in profile_containers:
            profile_info = {
                "URL": "Not Specified",
                "Name": "Not Specified",
                "Position": "Not Specified",
                "Company": "Not Specified",
                "Location": "Not Specified",
                "Periods": "Not Specified",
                "Department": "Not Specified"
            }

            # Extract URL
            try:
                profile_link = container.find_element(By.CSS_SELECTOR, "a")
                profile_info["URL"] = profile_link.get_attribute('href')
            except NoSuchElementException:
                print("Profile URL element not found.")

            # Extract Name
            try:
                name_element = container.find_element(By.CSS_SELECTOR, "h3")
                profile_info["Name"] = name_element.text.split(' - ')[0]
            except NoSuchElementException:
                print("Name element not found.")

            # Extract Position, Company, and Location
            try:
                details = container.find_element(By.CSS_SELECTOR, "div.LEwnzc.Sqrs4e").text.split(' · ')
                if len(details) >= 3:
                    profile_info["Location"] = details[0]
                    profile_info["Position"] = details[1]
                    profile_info["Company"] = details[2]
            except NoSuchElementException:
                print("Details element for Position, Company, or Location not found.")

            all_profiles.append(profile_info)

    except Exception as e:
        print(f"Error occurred while scraping profiles: {e}")

    return all_profiles

def scroll_page2(browser, role, bank, department, region):
    # Scrolls through the Google search results page and loads more results
    base_url = f"https://www.google.com/search?q=linkedin profile: {role} {department} {bank} {region} investment banking"
    browser.get(base_url)
    time.sleep(5)

    try:
        last_height = browser.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        while scroll_count < 1:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.5, 3.5))

            # Check for the "More search results" button and click if present
            try:
                more_results_button = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.T7sFge.sW9g3e.VknLRd"))
                )
                browser.execute_script("arguments[0].click();", more_results_button)
                time.sleep(random.uniform(1.5, 3.5))
            except TimeoutException:
                print("No more 'More search results' button found.")
                break

            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_count += 1

    except Exception as e:
        print(f"Error during scrolling: {e}")

def scrape_multiple_profiles2(browser, role, department, bank, region):
    scroll_page2(browser, role, department, bank, region)
    all_profiles = []

    try:
        # Locate all profile containers on the page
        profile_containers = browser.find_elements(By.CSS_SELECTOR, "div.tF2Cxc")

        for container in profile_containers:
            profile_info = {
                "URL": "Not Specified",
                "Name": "Not Specified",
                "Position": "Not Specified",
                "Company": "Not Specified",
                "Location": "Not Specified",
                "Periods": "Not Specified",
                "Department": "Not Specified",
            }

            # Extract URL
            try:
                profile_link = container.find_element(By.CSS_SELECTOR, "a")
                profile_info["URL"] = profile_link.get_attribute('href')
            except NoSuchElementException:
                print("Profile URL element not found.")

            # Extract Name
            try:
                name_element = container.find_element(By.CSS_SELECTOR, "h3")
                profile_info["Name"] = name_element.text.split(' - ')[0]
            except NoSuchElementException:
                print("Name element not found.")

            # Extract Position, Company, and Location
            try:
                details = container.find_element(By.CSS_SELECTOR, "div.LEwnzc.Sqrs4e").text.split(' · ')
                if len(details) >= 3:
                    profile_info["Location"] = details[0]
                    profile_info["Position"] = details[1]
                    profile_info["Company"] = details[2]
            except NoSuchElementException:
                print("Details element for Position, Company, or Location not found.")

            all_profiles.append(profile_info)

    except Exception as e:
        print(f"Error occurred while scraping profiles: {e}")

    return all_profiles

def profiles_to_excel(profiles, filename="LinkedIn_Profiles.xlsx"):
    profile_data_directory = os.path.join(os.getcwd(), "profile_data")

    filepath = os.path.join(profile_data_directory, filename)

    df = pd.DataFrame(profiles)
    df.to_excel(filepath, index=False)

    print(f"Data exported to {filepath}")