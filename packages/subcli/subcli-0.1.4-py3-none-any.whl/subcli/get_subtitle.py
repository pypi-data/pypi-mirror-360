import requests
import time
from bs4 import BeautifulSoup

def search_subtitle_options(movie_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
    }
    url = f'https://subtitlecat.com/index.php?search={movie_name.replace(" ", "+")}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching data from {url}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    
    tr = ((soup.find('div', class_='subtitles')).find('table', class_='table sub-table')).find('tbody').find_all('tr')

    results = {}

    for row in tr:
        tds = row.find_all('td')

        title = tds[0].find('a').text.strip()
        rurl = 'https://subtitlecat.com/'+tds[0].find('a')['href']
        nr_of_downloads = tds[2].text.strip()
        nr_of_languages = tds[3].text.strip()

        print(f"Title: {title},\nURL: {rurl},\nDownloads: {nr_of_downloads},\nLanguages: {nr_of_languages}")
        print('-' * 40)

        results[title] = (rurl, nr_of_downloads, nr_of_languages)
    
    if not results:
        print("No subtitles found.")
        return {}   
    print(f"Found {len(results)} subtitles for '{movie_name}':")
    return results

def get_subtitle_options(url, filename=None):
    if not filename: filename = time.strftime("%Y-%m-%d_%H-%M-%S") + '.zip'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching data from {url}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = soup.find('div', class_='all-sub').find_all('div', class_='row')[1].find_all('div', class_='sub-single')
    subtitles = {}
    for result in results:
        a = result.find('a')
        if a:
            link = 'https://subtitlecat.com'+a['href'] 
            language = result.find_all('span')[1].text.strip()
            subtitles[language] = link
    
    return subtitles

def download_subtitle(url, filename=None):
    if not filename: filename = url.split('/')[-1]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    with open(filename, 'wb') as file:
        file.write(response.content)
    return filename

print(search_subtitle_options("Ant-Man and The Wasp: Quantumania"))