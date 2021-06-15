import json
import scrapy


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["https://www.instagram.com/"]
    _login_path = "/accounts/login/ajax/"
    _tags_path = "/explore/tags/{tag}/"

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
            print(1)
            for tag in self.tags:
                yield response.follow(self._tags_path.format(tag=tag), callback=self.tag_page_parse)

    def tag_page_parse(self, response):
        print(1)

    def js_data_extract(self, response) -> dict:
        js = response.xpath("//script[contains(text(), 'window._sharedData =')]/text()").extract_first()
        js_data = json.loads(js[js.index("{") : -1])
        return js_data
