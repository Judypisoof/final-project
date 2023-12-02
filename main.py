import json
import time
import requests
from bs4 import BeautifulSoup

USE_CACHE = True
CACHE_FILE_NAME = 'web_url_cache.json'
CACHE_DICT = {}

MAIN_SITE = 'https://www.worldbeachguide.com'
BEACHES_BY_COUNTRY_URL = '/beach-destinations'
TOP_100_BEACHES_URL = '/top-100-beaches-earth.htm'

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def make_url_request_using_cache(url, cache):
    if url in cache.keys():
        print("Using cache: " + url)
        return cache[url]
    else:
        print("Fetching: " + url)
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]


def make_soup(url):
    if USE_CACHE:
        return BeautifulSoup(make_url_request_using_cache(url, CACHE_DICT), 'html.parser')
    else:
        return BeautifulSoup(requests.get(url).text, 'html.parser')


def get_beach_info(beach_url):
    print("getting beach info from " + MAIN_SITE + beach_url)
    beach_info = {}

    beach_page_soup = make_soup(MAIN_SITE + beach_url)

    beach_info['country'] = beach_page_soup.find(id='breadcrumbs').find_all('a')[1].text

    beach_info_section = beach_page_soup.find(id='info')

    beach_name = beach_info_section.find('h1').text
    beach_info['name'] = beach_name

    if beach_info_section.find(id='description') is not None:
        beach_info['description'] = ' '.join(
            p.text for p in beach_info_section.find(id='description').find_all('p'))
    else:
        beach_info['description'] = ''

    beach_info['near_town_or_city'] = beach_info_section.find('div', attrs={'class', 'col-md-6'}).find('p').text

    beach_weather_section = beach_page_soup.find(id='weather')

    beach_current_weather_div = beach_weather_section.find(id='current-weather')

    description = beach_current_weather_div.find('strong').text
    temperature = beach_current_weather_div.find('p').text.replace(description, '').replace('\n\t\t', '')

    beach_info['weather'] = {
        'description': description,
        'temperature': temperature,
        'sea-temperature': beach_weather_section.find('span', attrs={'class', 'seatemp'}).text
    }

    beach_info['rating'] = beach_page_soup.find(id='ratings-meta').text

    beach_info['near_beaches'] = list(
        map(lambda x: x.text, beach_page_soup.find('ul', id='near').find_all('li')))
    return beach_name, beach_info


def scrawl_country_best_beach_map_to_json():

    # get country's beach url list
    def get_beach_url_list_by_country(country_info_url, page_number):
        country_beach_url_list = []
        # iterate every page
        for page_index in range(1, page_number + 1):
            country_page_soup = make_soup(MAIN_SITE + country_info_url + '/' + str(page_index))
            country_beach_ul = country_page_soup.find('ul', attrs={'class', 'beach-list'})
            country_beach_li_list = country_beach_ul.find_all('li', id=True)
            country_beach_url_list += list(map(lambda x: x.find('a').attrs['href'], country_beach_li_list))

        return country_beach_url_list

    # get total page count of country beaches
    def get_page_number(country_page_soup):
        number = 1
        country_page_pagination = country_page_soup.find('ul',
                                                         attrs={'class', 'pagination pagination-circular text-center'})
        if country_page_pagination != None:
            last_pagination_button = country_page_pagination.find('li', attrs={'class', 'last'})
            if last_pagination_button is not None:
                number = int(last_pagination_button.find('a').attrs['data-ci-pagination-page'])
            else:
                number = len(country_page_pagination.find_all('li')) - 1

        return number

    beaches_by_country_soup = make_soup(MAIN_SITE + BEACHES_BY_COUNTRY_URL)

    country_ul = beaches_by_country_soup.find('ul', attrs={'class', 'row block-grid'})
    country_li_list = country_ul.find_all('li', attrs={'class', 'col-sm-6 col-lg-3'})

    country_info_dict = {}

    for x in country_li_list:
        country_info_dict[x.find('h3').text] = {'name': x.find('h3').text, 'url': x.find('a').attrs['href']}

    print("country info list: ", end='')
    print(country_info_dict.keys())

    for country_info in country_info_dict.values():

        print("getting {}'s beaches".format(country_info['name']))

        country_page_soup = make_soup(MAIN_SITE + country_info['url'])

        page_number = get_page_number(country_page_soup)

        country_beach_url_list = get_beach_url_list_by_country(country_info['url'], page_number)

        print("{} has {} best beaches".format(country_info['name'], len(country_beach_url_list)))

        country_beach_info_dict = {}

        # iterate every beach url
        country_rank = 1
        for beach_url in country_beach_url_list:
            beach_name, beach_info = get_beach_info(beach_url)
            beach_info['country_rank'] = country_rank
            country_rank += 1
            country_beach_info_dict[beach_name] = beach_info

        country_info['beaches'] = country_beach_info_dict

        time.sleep(0.1)

    country_info_json = json.dumps(country_info_dict, ensure_ascii=False)

    json_file = open('country_info.json', 'w', encoding='utf-8')
    json_file.write(country_info_json)
    json_file.close()


def scrawl_best_100_beaches_to_json():
    top_100_beaches_ul = make_soup(MAIN_SITE + TOP_100_BEACHES_URL).find('ul', attrs={'class', 'beach-list'})

    top_100_beaches_li = top_100_beaches_ul.find_all('li', id=True)

    top_100_beaches_url_list = list(map(lambda x: x.find('a').attrs['href'], top_100_beaches_li))

    top_100_beaches = {}
    world_rank = 100
    for beach_url in top_100_beaches_url_list:
        beach_name, beach_info = get_beach_info(beach_url)
        beach_info['world_rank'] = world_rank
        world_rank -= 1
        top_100_beaches[beach_name] = beach_info

    top_100_beaches_json = json.dumps(top_100_beaches, ensure_ascii=False)

    print(top_100_beaches_json)

    json_file = open('top_100_beaches.json', 'w', encoding='utf-8')
    json_file.write(top_100_beaches_json)
    json_file.close()


if __name__ == '__main__':
    if USE_CACHE:
        CACHE_DICT = load_cache()

    scrawl_country_best_beach_map_to_json()
    scrawl_best_100_beaches_to_json()
