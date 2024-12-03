scrapy crawl CompetitionSpider -O crawled_data/competitions.json --loglevel='ERROR'
scrapy crawl Clubtfmkt -a json_path="crawled_data/competitions.json" -O crawled_data/clubs.json
scrapy crawl Players -a json_path="crawled_data/clubs.json" -O crawled_data/players.json