import requests
from bs4 import BeautifulSoup
from config import Config as c


def search_movie(
        movie, 
        quality = c.QUALITY['all'], 
        genre = c.GENRES['all'], 
        year = '0', 
        rating = 0, 
        language = 'en', 
        order_by = 'latest'
        ):
    url = c.SEARCH_URL
    payload = {
        "keyword": movie,
        "quality": quality,
        "genre": genre,
        "rating": rating,
        "year": year,
        "language": language,
        "order_by": order_by
    }

    response = requests.post(url, data=payload)
    
    soup = BeautifulSoup(response.text, 'html.parser')

    browse_content = soup.find_all('div', class_='browse-content')[0]
    rows_div = browse_content.find_all('div', class_='row')[0]
    search_result = rows_div.find_all('div', recursive=False)

    results = []

    for div in search_result:
        bmt = div.find('a', class_='browse-movie-title')
        result_title = bmt.text
        result_link = bmt['href']
        result_cover = div.find('img', class_='img-responsive')['src']
        result_year = div.find('div', 'browse-movie-year').text
        result = (result_title, result_link, result_cover, result_year)
        results.append(result)
    
    return results

def get_movie_details(url):
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    with open('response.html', 'w') as f:
        print(soup.prettify(), file=f)
    
    movie_details = soup.find('div', id='movie-info')
    infos = movie_details.find_all('div', recursive=False)
    title = (infos[0].find('h1')).text
    year = infos[0].find_all('h2')[0].text
    categories = (infos[0].find_all('h2')[1].text).split('/')

    bottom_info = infos[1].find_all('div', class_='rating-row')

    tomatometer = bottom_info[1].find('span').text if len(bottom_info) > 1 else None
    audience = bottom_info[2].find('span').text if len(bottom_info) > 2 else None
    imdb = bottom_info[3].find('span').text if len(bottom_info) > 3 else None
    
    available_in = movie_details.find('p').find_all('a', recursive=False)

    downloads = {}

    for a in available_in:
        download_link = a['href']
        quality = a.text
        downloads[quality] = download_link
    
    return title, year, categories, tomatometer, audience, imdb, downloads

import requests
import os

def download_torrent(url, filename=None):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)

        if response.status_code != 200:
            print(f"Erro ao baixar: código {response.status_code}")
            return None

        if not filename:
            filename = url.split('/')[-1]
            if not filename.endswith('.torrent'):
                filename += '.torrent'

        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f"Arquivo salvo como: {filename}")
        return filename

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
