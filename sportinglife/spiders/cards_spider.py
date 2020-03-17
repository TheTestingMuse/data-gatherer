import os
import time
import re

import scrapy

# Remove existing racecards.json file
if os.path.exists("racecards.json"):
    os.remove("racecards.json")
else:
    print("The file does not exist")


def is_handicap(race_name):
    return "Handicap" in race_name or "Nursery" in race_name


# Define RaceDetails Item
class RaceDetails(scrapy.Item):
    raceMeeting = scrapy.Field()
    raceGoing = scrapy.Field()
    raceSurface = scrapy.Field()
    raceTime = scrapy.Field()
    raceName = scrapy.Field()
    raceHandicap = scrapy.Field()
    raceLink = scrapy.Field()
    runnersMinAge = scrapy.Field()
    runnersMaxAge = scrapy.Field()
    raceClass = scrapy.Field()
    raceLength = scrapy.Field()
    raceRunners = scrapy.Field()


class RacecardsSpider(scrapy.Spider):
    name = "racecards"
    allowed_domains = ["sportinglife.com"]
    start_urls = [
        "https://www.sportinglife.com/racing/racecards",
    ]

    def parse(self, response):
        # Define Valid Meeting names
        valid_meetings = [
            "Aintree", "Ascot", "Ayr", "Ballinrobe", "Bangor-On-Dee", "Bath", "Bellewstown",
            "Beverley", "Brighton", "Carlisle", "Cartmel", "Catterick", "Chelmsford City",
            "Cheltenham", "Chepstow", "Chester", "Clonmel", "Cork", "Curragh", "Doncaster",
            "Down Royal", "Downpatrick", "Dundalk", "Epsom Downs", "Exeter", "Fairyhouse",
            "Fakenham", "Ffos Las", "Folkestone", "Fontwell", "Galway", "Goodwood", "Gowran",
            "Great Leighs", "Hamilton", "Haydock", "Hereford", "Hexham", "Huntingdon", "Kelso",
            "Kempton", "Kilbeggan", "Killarney", "Laytown", "Leicester", "Leopardstown", "Limerick",
            "Lingfield", "Listowel", "Ludlow", "Market Rasen", "Musselburgh", "Naas", "Navan",
            "Newbury", "Newcastle", "Newmarket", "Newton Abbot", "Nottingham", "Perth", "Plumpton",
            "Pontefract", "Punchestown", "Redcar", "Ripon", "Roscommon", "Salisbury", "Sandown",
            "Sedgefield", "Sligo", "Southwell", "Stratford", "Taunton", "Thirsk", "Thurles",
            "Tipperary", "Towcester", "Tralee", "Tramore", "Uttoxeter", "Warwick", "Wetherby",
            "Wexford", "Wincanton", "Windsor", "Wolverhampton", "Worcester", "Yarmouth", "York",
        ]
        # Begin looping through cards for each Meeting on page
        for card in response.css("section.hr-meeting-container"):
            # Get Meeting-level data - Title, Going and Surface
            current_meeting = card.css("h2.sectionTitleWithProviderLogo a::text").get()
            going = card.css("div.hr-meeting-meta span.hr-meeting-meta-value::text").get()
            surface = card.css("div.hr-meeting-meta-surface span.hr-meeting-meta-value::text").get()

            # Check if Meeting is UK/IRE and loop through individual races
            if not any(s in current_meeting for s in valid_meetings):
                continue

            for race_item in card.css("ul.hr-meeting-races-container li"):
                # Get Meeting details
                r = RaceDetails()
                r["raceMeeting"] = current_meeting
                r["raceGoing"] = going
                r["raceSurface"] = surface

                # Get Races details
                r["raceTime"] = race_item.css("span.hr-meeting-race-time::text").get()
                r["raceName"] = race_item.css("div.hr-meeting-race-name-star::text").get()
                r["raceHandicap"] = (
                    "Handicap" if is_handicap(r["raceName"]) else "Non-Handicap"
                )
                race_link = race_item.css("a::attr(href)").get()
                r["raceLink"] = ("https://www.sportinglife.com" + race_link)

                # Split Ages, Classes, Race Length and Runners
                #race_details = race_item.css("div.hr-meeting-race-name-star span::text")[1].extract()
                ages, *extra, length, runners = re.split(r',\s', race_item.css("div.hr-meeting-race-name-star span::text")[1].extract())
                # TO DO: Remove "Yo" text and account for Range of years
                if " to " in ages:
                    # Split on " to " text
                    min_age, max_age = re.split(r'\sto\s', ages)

                    r["runnersMinAge"] = int(min_age.replace("yo", ""))
                    r["runnersMaxAge"] = int(max_age.replace("yo", ""))
                else:
                    # Min age only
                    r["runnersMinAge"] = int(ages.replace("yo+", ""))
                    r["runnersMaxAge"] = 999
                # Check if Class data is missing. Mark as Class 0 if so and bump element location
                r["raceClass"] = int(extra[0][-1]) if extra else 0
                r["raceLength"] = length
                r["raceRunners"] = int(runners.replace(" runners", ""))

                yield r
