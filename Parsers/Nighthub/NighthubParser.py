import requests
from bs4 import BeautifulSoup
import json


def get_manga_pages_urls(pages_count: int) -> None:
    url = "https://nighthub.me/explore/type-is-manga/sort-is-rating?page="
    manga_pages_urls = []
    counter = 0

    for i in range(1, pages_count):
        response = requests.get(url + f"{i}", )
        soup = BeautifulSoup(response.text, "lxml")
        data = soup.findAll("a", class_="d-block position-relative")
        for j in data:
            counter += 1
            manga_pages_urls.append("https://nighthub.me" + j.get("href"))

    print(counter)
    with open("urls", "w", encoding="utf-8") as f:
        json.dump(manga_pages_urls, f)


def get_manga_data(url: str) -> dict:
    output_data = {}
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    output_data["image_url"] = soup.find("img", class_="cover").get("src")

    output_data["name_rus"] = soup.find("div", class_="text-line-clamp fs-5 fw-bold").text.strip()
    output_data["name_eng"] = soup.select("div.attr > div.attr-value")[-1].text.strip().split("/")[0]

    output_data["author"] = ""

    data = soup.find("div", class_="fs-2 text-muted fw-medium d-flex align-items-center").text.strip().split("\n\n\n")
    output_data["manga_type"] = data[0]
    output_data["manga_release_year"] = int(data[1]) if data[1].isdigit() else ""

    output_data["manga_status"] = ""
    if not data[1].isdigit():
        output_data["manga_status"] = data[1]
    else:
        output_data["manga_status"] = data[2]

    if output_data["manga_status"] == "онгоинг":
        output_data["manga_status"] = "Ongoing"
    elif output_data["manga_status"] == "приостановлен":
        output_data["manga_status"] = "Frozen"
    elif output_data["manga_status"] == "завершён":
        output_data["manga_status"] = "Finished"
    else:
        output_data["manga_status"] = ""

    output_data["chapters_count"] = int(soup.find("span", class_="ms-1 badge rounded-pill bg-primary").text)

    output_data["age_rating"] = ""
    if data[len(data) - 1] in ["16+", "18+"]:
        output_data["age_rating"] = data[len(data) - 1]

    data = soup.find("collapse-multiple", class_="d-block tags")
    tags = []
    if data is not None:
        data = data.findAll("a")
        for i in range(5 if len(data) > 5 else len(data)):
            tags.append(data[i].text.strip().strip("#"))
    output_data["tags"] = tags

    data = soup.find("div", class_="markdown-style text-expandable-content")
    output_data["description"] = ""
    if data is not None:
        output_data["description"] = data.text.strip()

    output_data["score"] = float(soup.find("span", class_="rating-star-rate").text)

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
        except IndexError as e:
            print(e)
            continue

    with open("NighthubData.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


parse_website()
