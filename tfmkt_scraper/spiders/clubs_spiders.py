import re
import scrapy
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

class SpiderClubs(scrapy.Spider):
    name = "Clubtfmkt"
    allowed_domains = ["www.transfermarkt.com"]
    start_urls = ["https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1", 
                  "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1"] #.com and not .fr (choice)

    def __init__(self, club_name=None, user_agent=USER_AGENT, *args, **kwargs):
        super(SpiderClubs, self).__init__(*args, **kwargs)
        self.club_name = club_name
        self.user_agent = user_agent

    def start_requests(self):
        print("Starting requests...")
        for url in self.start_urls:
            print(f"Requesting URL: {url}")
            yield scrapy.Request(url, self.parse_league, headers={
                'User-Agent': self.user_agent})


    def parse_league(self, response) :
        # return scrapy.FormRequest.from_response(response,
        #         response, 
        #         formdata = {"SearchTerms" : self.club_name},
        #         callback=self.parse_club)
        yield from self.parse_club(response)
    
    def parse_club(self, response) :
        clubs = response.xpath("//tbody/tr/td[@class='rechts']/a")
        league = response.xpath("//header/div/h1/text()").get().replace("\n", "").replace(" ","")
        # print(clubs)
        for club in clubs :
            name = club.xpath("./@title").get()
            href = club.xpath("./@href").get()
            value = club.xpath("./text()").get()
            if name is not None : 
                yield {
                    "league" : league,
                    "name" : name,
                    "href" : href,
                    "value" : value
                }

