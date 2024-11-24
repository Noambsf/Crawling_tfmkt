#!/usr/bin/env/crawler python3
# -*- coding: utf-8 -*-
import re
import scrapy

class SpiderPlayers(scrapy.Spider):

    name = 'Players'
    allowed_domains = ['https://www.transfermarkt.com/']
    start_urls = ['https://www.transfermarkt.com/paris-saint-germain/kader/verein/583/saison_id/2024',
                  'https://www.transfermarkt.com/olympique-marseille/kader/verein/244/saison_id/2024']

    def __init__(self, club=None, *args, **kwargs):
        super(SpiderPlayers, self).__init__(*args, **kwargs)
        self.person = club
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
   
    def parse(self, response):
        for player in response.xpath("//div[@class='responsive-table']//table[@class='items']/tbody/tr"): # response.xpath('//table[@class="inline-table"]//a'):
            """Parcourir les td et recuperer les info dans l'ordre"""
            
            name= player.xpath('./td[2]//a/text()').get().replace("\n","").replace("  ","")
            age= player.xpath('./td[3]/text()').get()
            position=  player.xpath('./td[2]/table[@class="inline-table"]//tr[2]/td/text()').get().replace("\n","").replace("  ","")
            number= player.xpath('.//div[@class="rn_nummer"]/text()').get()
            value= player.xpath('./td[@class="rechts hauptlink"]/a/text()').get()
            href= player.xpath('./td[2]//a/@href').get()
            
            yield {
                "name" : name, "age" : age, "position" : position,
                "number" : number, "value" : value, "href": href
            }    
