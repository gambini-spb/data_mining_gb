import json
import requests


def get_categories():
    url = "https://5ka.ru/api/v2/categories/"
    response = requests.get(url)
    return response.json()


def get_special_offers(id):
    params = {"categories": id,
              "records_per_page": 99,
              "page": 1
              }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/90.0.4430.212 Safari/537.36"}
    response = requests.get("https://5ka.ru/api/v2/special_offers/", params=params, headers=headers)
    return response


categories = get_categories()

all_data: list = []

for category in categories:
    id = category["parent_group_code"]
    offers = get_special_offers(id).json()["results"]
    if offers:
        data: dict = {"name": category["parent_group_name"], "id": id,
                      "products": offers}
        all_data.append(data)


def save():
    for category in all_data:
        with open(f'category{category["id"]}.json', 'w', encoding='utf-8') as f:
            json.dump(category, f, ensure_ascii=False)


save()