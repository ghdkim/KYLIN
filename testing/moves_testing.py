import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def fetch_html(url):
    """Fetches HTML content from a given URL using requests."""
    response = requests.get(url)
    return response.text

def parse_html(html):
    """Parses HTML content to extract details of each article."""
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article', class_='post-has-image')
    all_moves = []

    for article in articles:
        moves_info = {
            "URL": article.find('a', href=True)['href'] if article.find('a', href=True) else "N/A",
            "Image": article.find('img')['src'] if article.find('img') else "N/A",
            "Title": article.find('h2', class_='entry-title').text.strip() if article.find('h2', class_='entry-title') else "N/A",
            "Description": article.find('p').text.strip() if article.find('p') else "N/A",
            "Date": article.find('time', class_='entry-date').text.strip() if article.find('time', class_='entry-date') else "N/A"
        }
        all_moves.append(moves_info)

    return all_moves

def moves_to_excel(profiles, filename="Moves_News.xlsx"):
    """Exports scraped data to an Excel file."""
    data_directory = os.path.join(os.getcwd(), "data")
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    filepath = os.path.join(data_directory, filename)
    df = pd.DataFrame(profiles)
    df.to_excel(filepath, index=False)
    print(f"Data exported to {filepath}")

# Main execution block
base_url = "https://fundselectorasia.com/people-moves/"
html_content = fetch_html(base_url)
profiles = parse_html(html_content)
if profiles:
    profiles = profiles[:-1]  # Remove the last item from the list before exporting
    moves_to_excel(profiles)
else:
    print("No data found to export.")
