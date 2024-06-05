import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import os

def news_nyta(url):
    world_news = []
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser", parse_only=SoupStrainer("article"))

    for index, item in enumerate(soup.find_all('a')):
        if ('cn.nytimes.com' not in item.attrs['href']) and ('espanol' not in item.attrs['href']):
            news = {}
            news["URL"] = "https://www.nytimes.com" + item.attrs['href']
            date = '-'.join(item.attrs['href'].split('/', 4)[1:4])
            world_news.append(news)

    for index, item in enumerate(soup.find_all('img')):
        world_news[index]["Image"] = ''.join(item.attrs['src'].split('?', 1)[0])

    for index, item in enumerate(soup.find_all('h3')):
        world_news[index]["Title"] = item.text

    for index, item in enumerate(soup.find_all('p')[::2]):
        world_news[index]["Description"] = item.text
        world_news[index]["Date"] = date

    for index, item in enumerate(world_news):
      if world_news[index]["Date"] == "video-world-asia":
        world_news.remove(world_news[index])

    return world_news

def news_etia(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser", parse_only=SoupStrainer("div",{'class':'clr flt topicstry story_list'}))

    month_dict = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06",
                  "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
    world_news = []

    for index, item in enumerate(soup.find_all('a')):
        # if ('cn.nytimes.com' not in item.attrs['href']) and ('espanol' not in item.attrs['href']):
        new = {}
        new["URL"] = "https://economictimes.indiatimes.com" + item.attrs['href']
        world_news.append(new)

    for index, item in enumerate(soup.find_all('img')):
        world_news[index]["Image"] = ''.join(item.attrs['src'].split('?', 1)[0])

    for index, item in enumerate(soup.find_all('h2')):
        world_news[index]["Title"] = item.text

    for index, item in enumerate(soup.find_all('p', class_="wrapLines l3")):
        world_news[index]["Description"] = item.text

    for index, item in enumerate(soup.find_all('time')):
        world_news[index]["Date"] = item.text[8:12] + '-' + month_dict[item.text[3:6]] + '-' + item.text[0:2]

    return world_news

def news_fx(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser",
                         parse_only=SoupStrainer("article", {'class': 'node node--type-article node--view-mode-article-list'}))

    month_dict = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                  "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    market_news = []

    for article in soup:
        new = {}
        # Extract URL
        a_tag = article.find('a', class_="icon-text")
        if a_tag and 'href' in a_tag.attrs:
            new["URL"] = "https://www.fx-markets.com" + a_tag['href']

        # Extract Image
        img_tag = article.find('img')
        if img_tag and 'src' in img_tag.attrs:
            new["Image"] = "https://www.fx-markets.com" + img_tag['src'].split('?', 1)[0]

        # Extract Title
        title_tag = article.find('h5', class_="article-title")
        if title_tag and title_tag.a:
            new["Title"] = title_tag.a.get_text(strip=True)

        # Extract Description
        desc_tag = article.find('p', class_="truncate-listing")
        if desc_tag:
            new["Description"] = desc_tag.get_text(strip=True).replace(u'\xa0', u' ')

        # Extract Date
        time_tag = article.find('time')
        if time_tag and 'datetime' in time_tag.attrs:
            date = time_tag['datetime']
            year, month, day = date.split('-')
            formatted_date = f"{year}-{month}-{day}"
            new["Date"] = formatted_date

        if new:
            market_news.append(new)

    return market_news

def news_etim(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser", parse_only=SoupStrainer("div",{'class':'clr flt topicstry story_list'}))

    month_dict = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06",
                  "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
    market_news = []

    for index, item in enumerate(soup.find_all('a')):
        # if ('cn.nytimes.com' not in item.attrs['href']) and ('espanol' not in item.attrs['href']):
        new = {}
        new["URL"] = "https://economictimes.indiatimes.com" + item.attrs['href']
        market_news.append(new)

    for index, item in enumerate(soup.find_all('img')):
        market_news[index]["Image"] = ''.join(item.attrs['src'].split('?', 1)[0])

    for index, item in enumerate(soup.find_all('h2')):
        market_news[index]["Title"] = item.text

    for index, item in enumerate(soup.find_all('p', class_="wrapLines l3")):
        market_news[index]["Description"] = item.text

    for index, item in enumerate(soup.find_all('time')):
        market_news[index]["Date"] = item.text[8:12] + '-' + month_dict[item.text[3:6]] + '-' + item.text[0:2]

    return market_news

def moves_to_excel(profiles, filename="News.xlsx"):
    data_directory = os.path.join(os.getcwd(), "data")

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    filepath = os.path.join(data_directory, filename)

    df = pd.DataFrame(profiles)
    df.to_excel(filepath, index=False)

    print(f"Data exported to {filepath}")