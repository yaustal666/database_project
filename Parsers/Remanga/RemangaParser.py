from ast import parse

import requests
from bs4 import BeautifulSoup
import json


def get_manga_pages_urls(pages_count: int) -> None:
    url = "https://remanga.org/manga?page="
    manga_pages_urls = []
    counter = 0

    for i in range(1, pages_count):
        response = requests.get(url + f"{i}")
        soup = BeautifulSoup(response.text, "lxml")

        data = soup.findAll("a", class_="Vertical_card__Qez7E")
        for j in data:
            counter += 1
            manga_pages_urls.append("https://remanga.org" + j.get("href"))

    print(counter)
    with open("urls", "w", encoding="utf-8") as f:
        json.dump(manga_pages_urls, f)


def get_manga_data(url: str) -> dict:
    output_data = {}

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    output_data["image_url"] = soup.find("div",
                                         class_="relative aspect-[2/3] overflow-hidden rounded-[16px] bg-[var(--bg-primary)] shadow-xl").find(
        "img").get("src")

    data = soup.find("h1", class_="Typography_h3___I3IT")
    output_data["name_rus"] = data.text
    output_data["name_eng"] = ""

    data = soup.find("div", {"class": "min-w-[60px] flex flex-col -space-y-1 pt-0.5", "itemprop": "publisher"})
    if data:
        output_data["author"] = data.find("p").text
    else:
        output_data["author"] = ""

    data = soup.find("div", class_="flex flex-col items-start gap-1").find("h5").text.split(" ")
    output_data["manga_type"] = data[0]
    output_data["manga_release_year"] = int(data[1])

    data = soup.findAll("p", class_="Typography_body1__YTqxB flex justify-center items-center whitespace-nowrap gap-2")
    output_data["manga_status"] = data[4].text

    if output_data["manga_status"] == "Продолжается":
        output_data["manga_status"] = "Ongoing"
    elif output_data["manga_status"] == "Заморожен":
        output_data["manga_status"] = "Frozen"
    elif output_data["manga_status"] == "Закончен":
        output_data["manga_status"] = "Finished"
    else:
        output_data["manga_status"] = ""

    output_data["chapters_count"] = int(data[0].text) if data[0].text.isdigit() else ""
    output_data["age_rating"] = data[-1].text

    data = soup.find("div", class_="flex flex-wrap -m-1").findAll("a")
    tags = []
    for i in range(7):
        tags.append(data[i].text)
    output_data["tags"] = tags

    data = soup.find("div", class_="Typography_body1__YTqxB")
    output_data["description"] = data.text

    data = soup.find("div", class_="flex flex-row items-end space-x-2").find("span")
    output_data["score"] = float(data.text)

    return output_data


def parse_website():
    data = []
    with open("urls", "r", encoding="utf-8") as file:
        manga_pages_urls = json.load(file)

    for i in manga_pages_urls:
        print(i)
        try:
            data.append(get_manga_data(i))
        except ValueError as e:
            print(e)
            continue

    with open("RemangaData.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


parse_website()
