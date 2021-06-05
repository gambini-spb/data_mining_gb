import scrapy
import pymongo


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    db = db_client["auto_parser"]

    def parse(self, response, **kwargs):
        print(1)
        for a_link in response.css(".TransportMainFilters_brandsList__2tIkv a.blackLink"):
            url = a_link.attrib.get("href")
            yield response.follow(url, callback=self.brand_parse)

    def brand_parse(self, response):
        for link in response.css(".Paginator_block__2XAPy a.Paginator_button__u1e7D"):
            url = link.attrib.get("href")
            yield response.follow(url, callback=self.brand_parse)

        for link in response.css("article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu"):
            url = link.attrib.get("href")
            yield response.follow(url, callback=self.car_parse)

    def car_parse(self, response):
        data: dict = {}
        # Название объявления
        data["title_car"] = response.css(".AdvertCard_advertTitle__1S1Ak ::text").extract_first()
        # Список фото объявления (ссылки)
        image_links: list = []
        for link in response.css(".PhotoGallery_block__1ejQ1 img"):
            image_links.append(link.attrib.get("src"))

        data["image_links"] = image_links
        # Список характеристик
        params_keys: list = []
        for div in response.css(".AdvertCard_specs__2FEHc div.AdvertSpecs_label__2JHnS ::text"):
            params_keys.append(div.extract())

        params: dict = {}
        for i, div in enumerate(response.css(".AdvertSpecs_data__xK2Qx *::text")):
            params[params_keys[i]] = div.extract()

        data["params"] = params
        # Описание объявления
        data["description"] = response.css(".AdvertCard_descriptionInner__KnuRi ::text").extract_first()

        # Ссылку на автора объявления и номер телефона достать не удалось

        self.save_data(data)

    def save_data(self, data):
        collection = self.db["auto"]
        collection.insert_one(data)
