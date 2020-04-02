import os
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
    raceLengthStr = scrapy.Field()
    raceLengthConv = scrapy.Field()
    raceRunners = scrapy.Field()


class RacecardsSpider(scrapy.Spider):
    name = "racecards"
    allowed_domains = ["sportinglife.com"]
    start_urls = [
        "https://www.sportinglife.com/racing/racecards/2020-01-03",
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
                r["raceTime"] = race_item.css("span.hr-meeting-race-time::text").get() # Race Time
                r["raceName"] = race_item.css("span.hr-meeting-race-name::text").get() # Race Name
                race_link = race_item.css("a::attr(href)").get()
                r["raceLink"] = ("https://www.sportinglife.com" + race_link)  # Link to Racecard
                r["raceHandicap"] = (
                    "Handicap" if is_handicap(r["raceName"]) else "Non-Handicap"
                ) # Race Handicap Status
                race_runners = race_item.css("span.hr-meeting-race-runners::text").get()
                new_race_runners = race_runners.split(" ")[0]
                r["raceRunners"] = int(new_race_runners) # Number of Runners
                race_class = race_item.css("span.hr-meeting-race-class::text").get()
                int_race_class = race_class.split(",")[0]
                race_class = int_race_class.replace("Class ", "")
                int_race_class = int(race_class) # Race Class
                if int_race_class > 0:
                    r["raceClass"] = int_race_class
                else:
                    r["raceClass"] = 0
                race_length = race_item.css("span.hr-meeting-race-distance::text").get()
                r["raceLengthStr"] = race_length # Original String of Race Length
                # Convert race lengths - 1m = 8f = 1760y
                if "m" in race_length and "f" in race_length and "y" in race_length:
                    miles, furlongs, yards = re.split(r'm\s|f\s', race_length)
                    conv_miles = int(miles.replace("m", "")) * 1760
                    conv_furlongs = int(furlongs.replace("f", "")) * 220
                    conv_yards = int(yards.replace("y", ""))
                    conv_length = conv_miles + conv_furlongs + conv_yards
                elif "m" in race_length and "f" in race_length:
                    miles, furlongs = re.split(r'm\s', race_length)
                    conv_miles = int(miles.replace("m", "")) * 1760
                    conv_furlongs = int(furlongs.replace("f", "")) * 220
                    conv_length = conv_miles + conv_furlongs
                elif "m" in race_length and "y" in race_length:
                    miles, yards = re.split(r'm\s', race_length)
                    conv_miles = int(miles.replace("m", "")) * 1760
                    conv_yards = int(yards.replace("y", ""))
                    conv_length = conv_miles + conv_yards
                elif "m" in race_length:
                    conv_miles = int(race_length.replace("m", "")) * 1760
                    conv_length = conv_miles
                elif "f" in race_length and "y" in race_length:
                    furlongs, yards = re.split(r'f\s', race_length)
                    conv_furlongs = int(furlongs.replace("f", "")) * 220
                    conv_yards = int(yards.replace("y", ""))
                    conv_length = conv_furlongs + conv_yards
                else:
                    furlongs = re.split(r'f\s', race_length)
                    conv_length = furlongs * 220
                r["raceLengthConv"] = conv_length # Conversion of Race Length for filtering

                yield r