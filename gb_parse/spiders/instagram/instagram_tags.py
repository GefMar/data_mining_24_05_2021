import json
from urllib.parse import urlencode

import scrapy


class InstagramTagsSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com", "i.instagram.com"]
    start_urls = ["https://www.instagram.com/"]
    _login_path = "/accounts/login/ajax/"
    _tags_path = "/explore/tags/{tag}/"
    _api_url = "/api/v1/tags/{tag}/sections/"

    def __init__(self, login, password, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                response.urljoin(self._login_path),
                method="POST",
                formdata={"username": self.login, "enc_password": self.password,},
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
                callback=self.parse,
            )
        except AttributeError:
            for tag in self.tags:
                yield response.follow(self._tags_path.format(tag=tag), callback=self.tag_page_parse)

    def tag_page_parse(self, response):
        js_data = self.js_data_extract(response)
        loader = InstagramDataLoader(js_data)
        yield from loader.recent_posts()
        print(1)
        post_body = loader.recent_pagination()
        # headers = response.request.headers
        headers = {}
        headers["X-CSRFToken"] = js_data["config"]["csrf_token"]
        yield response.follow(
            self._api_url.format(tag="python"),
            method="POST",
            cookies=response.request.cookies,
            callback=self.api_tag_parse,
            body=urlencode(post_body),
            headers=headers,
        )

    def api_tag_parse(self, response):
        print(1)

    def js_data_extract(self, response) -> dict:
        js = response.xpath("//script[contains(text(), 'window._sharedData =')]/text()").extract_first()
        js_data = json.loads(js[js.index("{") : -1])
        return js_data


class InstagramDataLoader:
    _mapper = {
        "recent_posts": ("entry_data", "TagPage", 0, "data", "recent", "sections"),
        "recent_data": ("entry_data", "TagPage", 0, "data", "recent"),
        "top_posts": ("entry_data", "TagPage", 0, "data", "top"),
    }

    def __init__(self, data: dict, mapper: dict = None):
        if mapper:
            self._mapper.update(mapper)
        self._data = data

    def _get_mapping_data(self, mapping_keys):
        data = self._data
        for key in mapping_keys:
            try:
                data = data[key]
            except Exception as e:
                # TODO: Тут надо ловить ошибку
                print(e)
        return data

    def recent_posts(self):
        for section in self._get_mapping_data(self._mapper["recent_posts"]):
            yield from map(
                lambda content: dict(item_type="post", **content["media"]), section["layout_content"]["medias"]
            )

    def recent_pagination(self):
        print(1)
        data = self._get_mapping_data(self._mapper["recent_data"])
        result = {
            "include_persistent": "0",
            "max_id": data["next_max_id"],
            "page": data["next_page"],
            "surface": "grid",
            "tab": "recent",
        }
        return result
