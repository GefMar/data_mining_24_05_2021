import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse.spiders.youla import AutoyoulaSpider
from gb_parse.spiders.hh import HhRemoteSpider
from gb_parse.spiders.instagram import InstagramTagsSpider


if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(
        InstagramTagsSpider, login=os.getenv("LOGIN"), password=os.getenv("PASSWORD"), tags=["python",]
    )
    # crawler_process.crawl(HhRemoteSpider)
    crawler_process.start()
