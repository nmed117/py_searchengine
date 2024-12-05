
from datetime import datetime
from os import path
import hashlib
import os

from bs4 import BeautifulSoup
from dateutil.parser import parse
from justext import justext
import nltk
import requests


def extract_content_and_links(url):
    stoplist = tuple(nltk.corpus.stopwords.words('english'))
    
    # Get the HTML content of the page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html5lib')

    date_element = soup.find('meta', {'property': 'article:published_time'})
    if date_element is not None:
        date_str = date_element['content']
        date = parse(date_str)
    else:
        date = None

    # Extract the text content of the page using justext
    paragraphs = justext(response.content, stoplist=stoplist)
    content = '\n'.join([p.text for p in paragraphs if not p.is_boilerplate])

    # Extract links from the page
    links = [a['href'] for a in soup.find_all('a') if 'href' in a.attrs]

    return content, links, date






def remove_stopwords(content):
    
    tokens = nltk.word_tokenize(content)
    filtered_tokens = [token.lower() for token in tokens if token.lower() not in stopwords]
    filtered_content = ' '.join(filtered_tokens)
    
    return filtered_content


def save_page_content(topic, url, content, date):
    # Calculate the hash value of the URL
    url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()

    # Create the topic related subfolder
    subfolder = 'data/' + topic

    # Create the subfolder if it doesn't exist
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    # Save the page content to a file
    try:
        with open(os.path.join(subfolder, f'{url_hash}.txt'), 'w', encoding='utf-8') as file:
            file.write(content)
    except UnicodeEncodeError:
        with open(os.path.join(subfolder, f'{url_hash}.txt'), 'w', encoding='utf-8', errors='ignore') as file:
            file.write(content)

    with open('crawl.log', 'a') as file:
        file.write(f'{topic}, {url}, {url_hash}, {date}\n')


nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('english')

with open('sources.txt', 'r') as file:
    sources = file.readlines()

for source in sources:
    topic, url = source.split(', ')
    topic = topic.strip()
    url = url.strip()

    content, links, date = extract_content_and_links(url)
    filtered_content = remove_stopwords(content)
    save_page_content(topic, url, filtered_content, date)

    for link in links:
        if link.startswith(url):
            content, links, date = extract_content_and_links(link)
            filtered_content = remove_stopwords(content)
            save_page_content(topic, link, filtered_content, date)


