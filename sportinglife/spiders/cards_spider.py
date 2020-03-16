import os
from typing import re

import scrapy
from yarl import URL

# Define base domain
url = URL('https://www.sportinglife.com')

# Remove existing racecards.json file
if os.path.exists("racecards.json"):
    os.remove("racecards.json")
else:
    print("The file does not exist")


# Define RaceDetails Item
class RaceDetails(scrapy.Item):
    raceMeeting = scrapy.Field()
    raceGoing = scrapy.Field()
    raceSurface = scrapy.Field()
    raceTime = scrapy.Field()
    raceName = scrapy.Field()
    raceHandicap = scrapy.Field()
    raceLink = scrapy.Field()
    runnersAge = scrapy.Field()
    raceClass = scrapy.Field()
    raceLength = scrapy.Field()
    raceRunners = scrapy.Field()


class RacecardsSpider(scrapy.Spider):
    name = "racecards"
    allowed_domains = ['www.sportinglife.com']
    start_urls = [
        'https://www.sportinglife.com/racing/racecards',
    ]

    def parse(self, response):
        # Define Valid Meeting names
        valid_meetings = ["Aintree", "Ascot", "Ayr", "Ballinrobe", "Bangor-On-Dee", "Bath", "Bellewstown",
                          "Beverley", "Brighton", "Carlisle", "Cartmel", "Catterick", "Chelmsford City", "Cheltenham",
                          "Chepstow",
                          "Chester", "Clonmel", "Cork", "Curragh", "Doncaster", "Down Royal", "Downpatrick",
                          "Dundalk", "Epsom Downs", "Exeter", "Fairyhouse", "Fakenham", "Ffos Las", "Folkestone",
                          "Fontwell", "Galway", "Goodwood", "Gowran", "Great Leighs", "Hamilton", "Haydock",
                          "Hereford", "Hexham", "Huntingdon", "Kelso", "Kempton", "Kilbeggan", "Killarney",
                          "Laytown", "Leicester", "Leopardstown", "Limerick", "Lingfield", "Listowel", "Ludlow",
                          "Market Rasen", "Musselburgh", "Naas", "Navan", "Newbury", "Newcastle", "Newmarket",
                          "Newton Abbot", "Nottingham", "Perth", "Plumpton", "Pontefract", "Punchestown", "Redcar",
                          "Ripon", "Roscommon", "Salisbury", "Sandown", "Sedgefield", "Sligo", "Southwell",
                          "Stratford", "Taunton", "Thirsk", "Thurles", "Tipperary", "Towcester", "Tralee", "Tramore",
                          "Uttoxeter", "Warwick", "Wetherby", "Wexford", "Wincanton", "Windsor", "Wolverhampton",
                          "Worcester", "Yarmouth", "York"]

        # Begin looping through cards for each Meeting on page
        for card in response.css('section.hr-meeting-container'):

            # Check Meeting Title to see if it's a UK/IRE race meet
            current_meeting = card.css('h2.sectionTitleWithProviderLogo a::text').get()

            # Begin looping through individual races
            if any(s in current_meeting for s in valid_meetings):

                # Get Meeting details
                r = RaceDetails()
                r["raceMeeting"] = card.css('h2.sectionTitleWithProviderLogo a::text').get()
                r["raceGoing"] = card.css('div.hr-meeting-meta span.hr-meeting-meta-value::text').get()
                r["raceSurface"] = card.css('div.hr-meeting-meta-surface span.hr-meeting-meta-value::text').get()
                r["raceTime"] = card.css('span.hr-meeting-race-time::text').get()

                temp_race_name = card.css('div.hr-meeting-race-name-star::text').get()
                r["raceName"] = temp_race_name
                if "Handicap" in temp_race_name or "Nursery" in temp_race_name:
                    r["raceHandicap"] = "Handicap"
                else:
                    r["raceHandicap"] = "Non-Handicap"

                r["raceLink"] = 'https://www.sportinglife.com' + card.css(
                    'ul.hr-meeting-races-container a::attr(href)').extract_first()
                r["runnersAge"] = card.css('div.hr-meeting-race-name-star span::text')[1].extract().split(",")[0]

                # TO DO: Remove "Yo" text and account for Range of years

                # Check if Class data is missing. Mark as Class 0 if so and bump element location
                temp_race_class = card.css('div.hr-meeting-race-name-star span::text')[1].extract().split(", ")[1]
                if "Class" in temp_race_class:
                    r["raceClass"] = temp_race_class[-1]
                    r["raceLength"] = card.css('div.hr-meeting-race-name-star span::text')[1].extract().split(", ")[2]
                    temp_race_runners = card.css('div.hr-meeting-race-name-star span::text')[1].extract().split(", ")[
                        3].replace(' runners', '')
                    r["raceRunners"] = temp_race_runners
                else:
                    r["raceClass"] = "0"
                    r["raceLength"] = card.css('div.hr-meeting-race-name-star span::text')[1].extract().split(", ")[1]
                    temp_race_runners = card.css('div.hr-meeting-race-name-star span::text')[1].extract().split(", ")[
                        2].replace(' runners', '')
                    r["raceRunners"] = temp_race_runners

                yield r
