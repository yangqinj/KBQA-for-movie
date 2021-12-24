"""
@author: Qinjuan Yang
@time: 2021-12-21 22:00
@desc: 
"""
import json
import os
import random
import requests
import string

from bs4 import BeautifulSoup
import re

base_url = "https://movie.douban.com"
top250_url = base_url + "/top250?start={}&filter="
movie_url = base_url + "/subject/"
celebrity_url = base_url + "/celebrity/"

celebrity_pattern = re.compile(r"/celebrity/([\d]+)/")
movie_pattern = re.compile(f"{movie_url}([\d]+)/")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

cookies = {
    "Cookie": f"bid={random.sample(string.ascii_letters + string.digits, 11)}"
}


data_dir = "../data/"
file_name_top250_movies_link = "top250_movies_urls.txt"


def send_request(url, retry=1):
    global cookies

    resp = requests.get(url, headers=headers, cookies=cookies)
    if resp.status_code != 200 and retry > 0:
        for _ in range(retry):
            if resp.status_code == 403:
                cookies = {
                    "Cookie": f"bid={random.sample(string.ascii_letters + string.digits, 11)}"
                }
            resp = requests.get(url, headers=headers, cookies=cookies)
            if resp.status_code == 200:
                break

    if resp.status_code != 200:
        print(f"Fail to get response from {url}")

    return None if resp.status_code != 200 else resp


def get_top250_movies():
    """
    Get url of Top250 movies and store them to the file.
    :return:
    """
    links = []
    for start in range(0, 250, 25):
        print(f"Crawling url for movies from {start} to {start + 25}")
        resp = requests.get(top250_url.format(start), headers=headers, cookies=cookies)
        if resp.status_code != 200:
            print("Error to get top250 movie list: status_code =", resp.status_code)
            continue

        # parse html to get url for top250 movies
        soup = BeautifulSoup(resp.text, 'html.parser')
        links.extend([a.attrs["href"] for a in soup.find_all(href=re.compile(movie_url))])

    links = set(links)
    print(f"Get {len(links)} movie links in total.")

    with open(os.path.join(data_dir, file_name_top250_movies_link), "w") as file:
        for l in links:
            file.write(l + "\n")


def get_movie_detail(movie_id):
    """
    Get detail of a single movie with title, rate, publish date and etc.
    :param url:
    :return:
    """

    resp = send_request(movie_url + movie_id)
    if not resp:
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    detail = {
        "id": movie_id
    }
    # find title
    title = soup.find("span", property="v:itemreviewed")
    detail["title"] = title.text.split(" ")[0]
    # find publish year
    year = soup.find("span", class_="year")
    if year:
        detail["year"] = re.search(r"[\d]{4}", year.text).group()
    # find directors
    directors = soup.find_all("a", rel="v:directedBy")
    if directors:
        detail["directors"] = []
        for d in directors:
            res = celebrity_pattern.match(d.attrs["href"])
            if res:
                detail["directors"].append(res.group(1))
    # find actors
    actors = soup.find_all("a", rel="v:starring")
    if actors:
        detail["actors"] = []
        for a in actors:
            res = celebrity_pattern.match(a.attrs["href"])
            if res:
                detail["actors"].append(res.group(1))
    # find genre
    genres = soup.find_all('span', property="v:genre")
    if genres:
        detail["genre"] = [g.text for g in genres]
    # find country
    country = soup.find("span", text="制片国家/地区:")
    if country:
        detail["country"] = country.next_sibling[1:]
    # find rate
    rate = soup.find("strong", property="v:average")
    if rate:
        detail["rate"] = rate.text

    return detail


def get_celebrity_detail(celebrity_id):
    resp = send_request(celebrity_url + celebrity_id)
    if not resp:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    detail = {
        "id": celebrity_id
    }
    # find name
    name = soup.find("h1")
    detail["name"] = name.text.split()[0]
    # find gender
    gender = soup.find("span", text="性别")
    if gender:
        detail["gender"] = gender.next_sibling[1:].strip()
    # find birth date
    birth_date = soup.find("span", text="出生日期")
    if birth_date:
        detail["birth_date"] = birth_date.next_sibling[1:].strip()
    else:
        birth_date = soup.find("span", text="生卒日期")
        if birth_date:
            detail["birth_date"] = birth_date.text.split("至")[0].strip()
    # find birth place
    birth_place = soup.find("span", text="出生地")
    if birth_place:
        detail["birth_place"] = birth_place.next_sibling[1:].strip()

    return detail


if __name__ == '__main__':
    # get_top250_movies()

    # Crawl details of movie and its actors and directors.
    # Store the detail in separate files where each line corresponds
    # for a single movie/actor/director in json format.
    with open(os.path.join(data_dir, file_name_top250_movies_link), "r") as file_link, \
            open(os.path.join(data_dir, "movie.json"), "w") as file_movie, \
            open(os.path.join(data_dir, "movie_to_celebrity.txt"), "w") as file_rel:

        celebrity_all = {}
        for x, link in enumerate(file_link):
            link = link.strip()
            if not link: continue

            # crawl detail of the movie
            print("Crawl detail of movie", x, link)
            movie_id = movie_pattern.match(link).group(1)
            movie_detail = get_movie_detail(movie_id)
            if not movie_detail:
                print(f"Fail to get detail of movie {link}")
                continue

            if "directors" in movie_detail:
                for d in movie_detail["directors"]:
                    # add relation for movie and director
                    file_rel.write("{} directedBy {}\n".format(movie_id, d))
                    celebrity_all[d] = 1
            if "actors" in movie_detail:
                for a in movie_detail["actors"]:
                    # add relation for movie and actor
                    file_rel.write("{} starring {}\n".format(movie_id, a))
                    celebrity_all[a] = 1

            # store movie detail to file
            file_movie.write(json.dumps(movie_detail, ensure_ascii=False) + "\n")

        # store celebrity
        with open(os.path.join(data_dir, "celebrity_id.txt"), "w") as file:
            file.write("\n".join(celebrity_all.keys()))

    with open(os.path.join(data_dir, "celebrity_id.txt"), "r") as file:
        celebrity_ids_all = [line.strip() for line in file.readlines() if line.strip()]

    with open(os.path.join(data_dir, "celebrity.json"), "a+") as file_celebrity:
        # craw detail of directors and actors
        for x, c in enumerate(celebrity_ids_all):
            print("Crawling celebrity", x, c)
            celebrity_detail = get_celebrity_detail(c)
            if not celebrity_detail:
                print(f"Fail to get detail of celebrity {c}")
                continue

            # store director detail to file
            file_celebrity.write(json.dumps(celebrity_detail, ensure_ascii=False) + "\n")

