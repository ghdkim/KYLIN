import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def parse_date(date_str):
    """ Helper function to parse date strings into datetime objects """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None  # Return None for invalid or missing date strings

def citiglobal():
    base_url = "https://webb-site.com/dbpub/SFClicensees.asp?p=18311"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    all_profiles = []
    last_profile_info = None  # To keep track of the last person with a name and URL

    try:
        # Locate all profile containers on the page within the table
        profile_containers = soup.find('table', class_='opltable').find_all('tr')[1:]  # Skipping the header

        for row in profile_containers:
            cols = row.find_all('td')
            if not cols[1].text.strip():  # If there is no name in the second column, it's a continuation row
                if last_profile_info and len(cols) > 5:
                    new_from_date = parse_date(cols[5].text.strip())
                    if new_from_date and last_profile_info['Periods'] != "Not Specified":
                        last_from_str, _ = last_profile_info['Periods'].split(' - ')
                        last_from_date = parse_date(last_from_str)
                        if last_from_date and new_from_date > last_from_date:
                            new_period = f"{cols[5].text.strip()} - {cols[6].text.strip() if cols[6].text.strip() else 'Present'}"
                            last_profile_info['Periods'] = new_period
                    continue

            # New profile info or first row for a person
            profile_info = {
                "URL": "Not Specified",
                "Name": "Not Specified",
                "Periods": "Not Specified",
                "Company": "Citigroup Global Markets Asia Limited",
                "Location": "Hong Kong"
            }

            # Extract URL and Name
            link_tag = cols[1].find('a')
            if link_tag:
                href = link_tag.get('href')
                profile_info["URL"] = f"https://webb-site.com/dbpub/{href}"
                name_text = link_tag.text.split(' (')[0]  # Splitting out any trailing designation
                name_parts = re.sub(r"\([^)]*\)", "", name_text).split(',')  # Remove anything in parentheses
                if len(name_parts) == 2:
                    profile_info["Name"] = f"{name_parts[1].strip()} {name_parts[0].strip()}"

            # Extract the From and Until dates
            if len(cols) > 5:
                from_date = cols[5].text.strip()
                until_date = cols[6].text.strip() if cols[6].text.strip() else "Present"
                period = f"{from_date} - {until_date}"
                # Always keep only the most recent period
                if profile_info['Periods'] != "Not Specified":
                    existing_from_str, _ = profile_info['Periods'].split(' - ')
                    existing_from_date = parse_date(existing_from_str)
                    new_from_date = parse_date(from_date)
                    if new_from_date and existing_from_date and new_from_date > existing_from_date:
                        profile_info['Periods'] = period
                else:
                    profile_info['Periods'] = period

            all_profiles.append(profile_info)
            last_profile_info = profile_info  # Update the last profile info

    except Exception as e:
        print(f"Error occurred while scraping profiles: {e}")

    return all_profiles

def hsbc():
    base_url = "https://webb-site.com/dbpub/SFClicensees.asp?p=50862"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    all_profiles = []
    last_profile_info = None  # To keep track of the last person with a name and URL

    try:
        # Locate all profile containers on the page within the table
        profile_containers = soup.find('table', class_='opltable').find_all('tr')[1:]  # Skipping the header

        for row in profile_containers:
            cols = row.find_all('td')
            if not cols[1].text.strip():  # If there is no name in the second column, it's a continuation row
                if last_profile_info and len(cols) > 5:
                    new_from_date = parse_date(cols[5].text.strip())
                    if new_from_date and last_profile_info['Periods'] != "Not Specified":
                        last_from_str, _ = last_profile_info['Periods'].split(' - ')
                        last_from_date = parse_date(last_from_str)
                        if last_from_date and new_from_date > last_from_date:
                            new_period = f"{cols[5].text.strip()} - {cols[6].text.strip() if cols[6].text.strip() else 'Present'}"
                            last_profile_info['Periods'] = new_period
                    continue

            # New profile info or first row for a person
            profile_info = {
                "URL": "Not Specified",
                "Name": "Not Specified",
                "Periods": "Not Specified",
                "Company": "HSBC Corporate Finance (Hong Kong) Limited",
            }

            # Extract URL and Name
            link_tag = cols[1].find('a')
            if link_tag:
                href = link_tag.get('href')
                profile_info["URL"] = f"https://webb-site.com/dbpub/{href}"
                name_text = link_tag.text.split(' (')[0]  # Splitting out any trailing designation
                name_parts = re.sub(r"\([^)]*\)", "", name_text).split(',')  # Remove anything in parentheses
                if len(name_parts) == 2:
                    profile_info["Name"] = f"{name_parts[1].strip()} {name_parts[0].strip()}"

            # Extract the From and Until dates
            if len(cols) > 5:
                from_date = cols[5].text.strip()
                until_date = cols[6].text.strip() if cols[6].text.strip() else "Present"
                period = f"{from_date} - {until_date}"
                # Always keep only the most recent period
                if profile_info['Periods'] != "Not Specified":
                    existing_from_str, _ = profile_info['Periods'].split(' - ')
                    existing_from_date = parse_date(existing_from_str)
                    new_from_date = parse_date(from_date)
                    if new_from_date and existing_from_date and new_from_date > existing_from_date:
                        profile_info['Periods'] = period
                else:
                    profile_info['Periods'] = period

            all_profiles.append(profile_info)
            last_profile_info = profile_info  # Update the last profile info

    except Exception as e:
        print(f"Error occurred while scraping profiles: {e}")

    return all_profiles

def profiles_to_excel(profiles, filename="LinkedIn_Profiles.xlsx"):
    profile_data_directory = os.path.join(os.getcwd(), "profile_data")

    filepath = os.path.join(profile_data_directory, filename)

    df = pd.DataFrame(profiles)
    df.to_excel(filepath, index=False)

    print(f"Data exported to {filepath}")