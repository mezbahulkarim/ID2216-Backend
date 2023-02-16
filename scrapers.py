from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import base64

# For requirements.txt, add these:
# beautifulsoup4
# urllib

def based64(input: str):
    encoded_to_ascii = input.encode("ascii")
    encoded_to_bytes = base64.urlsafe_b64encode(encoded_to_ascii)
    encoded_bytes_to_string = encoded_to_bytes.decode("ascii")
    encoded_bytes_to_string = encoded_bytes_to_string.replace('/', 'SLASH')
    return encoded_bytes_to_string


def search_movie(value: str):
    url = f"https://www.themoviedb.org/search/movie?query={value}"
    url=" ".join(url.split())
    url= url.replace(' ', '%20')
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    page_soup = BeautifulSoup(webpage, "html.parser")
    movies = page_soup.find_all("div", id=lambda value: value and value.startswith("card_movie"))

    all_movies = []
    for movie in movies:
        obj = {}
        try:
            movie_link = 'https://www.themoviedb.org' + movie.find("a")['href']
        except:
            continue
        try:
            movie_id = movie.find('a').get('data-id')
        except:
            continue
        try:
            image_url = 'https://www.themoviedb.org' + movie.find('div', class_='poster').find("img")['src']
        except:
            image_url = ''
        try:
            title = movie.find("h2").text
        except:
            title = ''

        link_encoded = based64(movie_link)

        obj['title'] = title
        obj['image_url'] = image_url
        obj['link'] = movie_link
        obj['link_encoded'] = link_encoded
        obj['id'] = movie_id
        
        all_movies.append(obj)
        
    return all_movies


async def detail_movie(link: str):
    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    page_soup = BeautifulSoup(webpage, "html.parser")
    
    final = {}
    
    title = page_soup.find('div', class_="title").find('h2').find('a').text.strip()
    release_date = page_soup.find('div', class_="title").find('h2').find('span').text.strip()
    image_url = 'https://www.themoviedb.org' + page_soup.find('img', class_="poster")['data-src'].strip()
    genre = page_soup.find('span', class_="genres").text.strip()
    
    length = page_soup.find('span', class_="runtime").text.strip()
    length = length.split(' ')
    hours = int(length[0].replace('h', ''))
    minutes = int(length[1].replace('m', ''))
    length = (hours * 60) + minutes
    
    description = page_soup.find('div', class_="overview").find('p').text.strip()
    
    overview_people = page_soup.find('div', class_="header_info").find('ol', class_=lambda value: value and value.startswith("people")).find_all('li', class_="profile")
    director = ''
    screenplay = ''
    for overview_person in overview_people:
        if 'Director' in overview_person.find('p', class_="character").text.strip():
            print('hello')
            director = overview_person.find('p').text.strip()
        elif 'Screenplay' in overview_person.find('p', class_="character").text.strip():
            print('hello 2')
            screenplay = overview_person.find('p').text.strip()

    
    actors = page_soup.find('section', class_="panel").find('ol', class_=lambda value: value and value.startswith("people")).find_all('li', class_="card")
    top_actors = []
    i = 0
    for actor in actors:
        if i > 5:
            break
        real_name = actor.find('p').text.strip()
        movie_name = actor.find('p', class_="character").text
        image_url = 'https://www.themoviedb.org' + actor.find('img')['src'].strip()
        obj = {}
        obj['real_name'] = real_name
        obj['movie_name'] = movie_name
        obj['image_url'] = image_url
        
        top_actors.append(obj)
        i += 1
    
    link_encoded = based64(link)

    final['title'] = title
    final['release_date'] = release_date
    final['image_url'] = image_url
    final['genre'] = genre
    final['length'] = length
    final['description'] = description
    final['actors'] = top_actors
    final['director'] = director
    final['screenplay'] = screenplay
    final['link'] = link
    final['link_encoded'] = link_encoded
    final['id'] = link.split('/')[-1]

    return final



def search_game(value: str):
    url = f"https://store.steampowered.com/search/?term={value}&ndl=1"
    url=" ".join(url.split())
    url= url.replace(' ', '%20')
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    page_soup = BeautifulSoup(webpage, "html.parser")
    games = page_soup.find("div", id="search_result_container").find_all('a')

    all_games = []
    for game in games:
        obj = {}
        
        try:
            title = game.find('span', class_="title").text
        except:
            continue
        try:
            game_link = game['href']
        except:
            continue
        try:
            game_id = game['data-ds-itemkey']
        except:
            continue 
        try:
            image_url = game.find('img')['src']
        except:
            image_url = ''

        link_encoded = based64(game_link)

        obj['title'] = title
        obj['image_url'] = image_url
        obj['link'] = game_link
        obj['link_encoded'] = link_encoded
        obj['id'] = game_id
        
        all_games.append(obj)

        
    return all_games


def detail_game(link: str):
    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    page_soup = BeautifulSoup(webpage, "html.parser")
    
    final = {}
    
    title = page_soup.find('div', class_="apphub_AppName").text.strip()
    image_url = page_soup.find('img', class_="game_header_image_full")['src']
    description = page_soup.find('div', class_="game_description_snippet").text.strip()
    release_date = page_soup.find('div', class_="date").text.strip()
    developer = page_soup.find('div', class_="dev_row").find('a').text.strip()
    publisher = page_soup.find_all('div', class_="dev_row")[1].find('a').text.strip()
    all_genres = page_soup.find('div', class_=lambda value: value and value.startswith("glance_tags")).find_all('a')
    genres = []
    i = 0
    for genre in all_genres:
        if i > 5:
            break
        genres.append(genre.text.strip())
        i += 1

    link_encoded = based64(link)
    
    final['title'] = title
    final['image_url'] = image_url
    final['description'] = description
    final['release_date'] = release_date
    final['developer'] = developer
    final['publisher'] = publisher
    final['genres'] = genres
    final['link'] = link
    final['link_encoded'] = link_encoded

    return final


def search_book(value: str):
    url = f"https://www.goodreads.com/search?q={value}&qid="
    url=" ".join(url.split())
    url= url.replace(' ', '%20')
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    page_soup = BeautifulSoup(webpage, "html.parser")
    books = page_soup.find("table").find_all('tr')

    all_books = []
    for book in books:
        obj = {}
        
        title = book.find('a', class_="bookTitle").text.strip()
        image_url = book.find('img')['src']
        book_link = 'https://www.goodreads.com/' + book.find('a', class_="bookTitle")['href']
        book_id = book.find('td').find('div')['id']
    
        link_encoded = based64(book_link)
        
        obj['title'] = title
        obj['image_url'] = image_url
        obj['link'] = book_link
        obj['link_encoded'] = link_encoded
        obj['id'] = book_id

        all_books.append(obj)

        
    return all_books


def detail_book(link: str):
    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    page_soup = BeautifulSoup(webpage, "html.parser")
    
    final = {}
    
    title = page_soup.find('h1').text.strip()
    author = page_soup.find('span', class_="ContributorLink__name").text.strip()
    image_url = page_soup.find('img', class_="ResponsiveImage")['src']
    description = page_soup.find('div', class_="DetailsLayoutRightParagraph").text.strip()
    publication_info = page_soup.find('div', class_="FeaturedDetails").find_all('p')[1].text.strip()
    
    all_genres = page_soup.find('div', class_="BookPageMetadataSection__genres").find_all('span', class_="BookPageMetadataSection__genreButton")
    genres = []
    i = 0
    for genre in all_genres:
        if i > 5:
            break
        genres.append(genre.text.strip())
        i += 1
    
    pages = page_soup.find('div', class_="FeaturedDetails").text.strip()
    pages = pages.split(' ')[0]
    
    book_id = link.split('/')[-1].split('-')[0]
    
    link_encoded = based64(link)

    final['title'] = title
    final['author'] = author
    final['image_url'] = image_url
    final['description'] = description
    final['publication_info'] = publication_info
    final['genres'] = genres
    final['pages'] = pages
    final['link'] = link
    final['link_encoded'] = link_encoded
    final['id'] = book_id

    return final