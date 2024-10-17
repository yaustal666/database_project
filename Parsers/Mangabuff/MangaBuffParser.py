import requests
from bs4 import BeautifulSoup
import json


def get_manga_pages_urls(pages_count: int) -> None:
    url = "https://mangabuff.ru/manga?page="
    manga_pages_urls = []
    counter = 0

    for i in range(1, pages_count):
        response = requests.get(url + f"{i}")
        soup = BeautifulSoup(response.text, "lxml")

        data = soup.findAll("a", class_="cards__item")
        for j in data:
            counter += 1
            manga_pages_urls.append(j.get("href"))

    print(counter)
    with open("urls", "w", encoding="utf-8") as f:
        json.dump(manga_pages_urls, f)


def get_manga_data(url: str) -> dict:
    output_data = {}

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    output_data["image_url"] = "https://mangabuff.ru" + soup.find("div", class_="manga__img").find("img").get("src")
    data = soup.find("div", class_="manga__names mb-2")
    output_data["name_rus"] = data.find("h1").text
    output_data["name_eng"] = data.find("span").text

    output_data["author"] = ""

    data = soup.find("div", class_="manga__middle-links mb-2").text.strip("\n").split("\n")
    output_data["manga_type"] = data[0]
    output_data["manga_release_year"] = int(data[1])
    output_data["manga_status"] = data[2]

    if output_data["manga_status"] == "Продолжается":
        output_data["manga_status"] = "Ongoing"
    elif output_data["manga_status"] == "Заморожен":
        output_data["manga_status"] = "Frozen"
    elif output_data["manga_status"] == "Завершен":
        output_data["manga_status"] = "Finished"
    else:
        output_data["manga_status"] = ""

    output_data["chapters_count"] = int(soup.find("button", {"class": "tabs__item", "data-page": "chapters"}).text.strip(
        "Главы ()"))

    tags = soup.find("div", {"class": "tags mb-4"}).text.strip().split("\n")[:8]
    output_data["age_rating"] = ""
    if tags[0] == "16+" or tags[0] == "18+":
        output_data["age_rating"] = tags.pop(0)
    output_data["tags"] = tags

    output_data["description"] = soup.find("div", class_="manga__description").text
    output_data["score"] = float(soup.find("div", class_="manga__rating").text)

    return output_data


def parse_website():
    data = []
    with open("urls", "r", encoding="utf-8") as file:
        manga_pages_urls = json.load(file)

    for i in manga_pages_urls:
        print(i)
        try:
            data.append(get_manga_data(i))
        except AttributeError as e:
            print(e)
            continue

    with open("MangabuffData.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


parse_website()
