#!/usr/bin/env/crawler python3
# -*- coding: utf-8 -*-
import re
import scrapy
import os
import json

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

class SpiderPlayers(scrapy.Spider):

    name = 'Players'
    allowed_domains = ["www.transfermarkt.com"]
    start_urls = ['https://www.transfermarkt.com/olympique-marseille/kader/verein/244/saison_id/2024']

    def __init__(self, json_path = str(None), club=None, user_agent=USER_AGENT, *args, **kwargs):
        super(SpiderPlayers, self).__init__(*args, **kwargs)
        self.user_agent = user_agent
        self.person = club
        if os.path.exists(json_path) :
            self.start_urls = self.load_clubs_urls(json_path)
            
    def load_clubs_urls(self, json_path) :
        club_urls = []
        with open(json_path, "r", encoding='utf-8') as file :
            clubs = json.load(file)
        for club in clubs : 
            club_urls.append(club['href'])
        return club_urls
    
    def start_requests(self):
        print("Starting requests...")
        for url in self.start_urls:
            print(f"Requesting URL: {url}")
            yield scrapy.Request(url, self.parse_club, headers={
                'User-Agent': self.user_agent})


    def parse_club(self, response):
        self.logger.info(f"Parsing club: {response.url} with status {response.status}")
        if response.status == 200:
            yield from self.parse_players(response)
        else:
            self.logger.error(f"Failed to retrieve {response.url} with status {response.status}")
    
    def parse_players(self, response):
        for player in response.xpath("//div[@class='responsive-table']//table[@class='items']/tbody/tr"):
            """Parcourir les td et recuperer les info dans l'ordre"""
            
            name= player.xpath('./td[2]//a/text()').get().replace("\n","").replace("  ","")
            team = player.xpath('//header[@class="data-header"]/div/h1/text()').get().replace("\n","").replace("  ","")
            age= player.xpath('./td[3]/text()').get()
            position=  player.xpath('./td[2]/table[@class="inline-table"]//tr[2]/td/text()').get().replace("\n","").replace("  ","")
            country = player.xpath('.//img[@class="flaggenrahmen"]/@title').get()
            number= player.xpath('.//div[@class="rn_nummer"]/text()').get()
            value= player.xpath('./td[@class="rechts hauptlink"]/a/text()').get()
            href= player.xpath('.//td[@class="hauptlink"]/a/@href').get()
            
            yield {
                "name" : name, "team" : team, "age" : age, "position" : position, "country" : country,
                "number" : number, "value" : value, "href": href
            }

            