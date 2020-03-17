import json
import scrapy

class RacesSpider(scrapy.Spider):
    name = "races"
    allowed_domains = ["sportinglife.com"]
    start_urls = []

    racecards_list = open("racecards.json","r")
    for url in racecards_list:
        start_urls.append(url)

    def start_requests(self):
        for url in self.start_urls:
            # Call function to manipulate url
            new_url = reformat_url(url)

        yield self.make_requests_from_url(new_url)


    def reformat_url(url):
    # Get URL's from json file
    url = json.loads(racecards_list['raceLink'])

    def parse(self, response):
    # Parse url response page

    racecards_list.close()