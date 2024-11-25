import scrapy
import re
from scrapy.exceptions import CloseSpider

class CompetitionSpider(scrapy.Spider):
    name = "CompetitionSpider"
    allowed_domains = ["transfermarkt.com"]
    start_urls = ["https://www.transfermarkt.com/wettbewerbe/europa"]

    custom_settings = {
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                      "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        'DOWNLOAD_DELAY': 1,  # To prevent being blocked
        'ROBOTSTXT_OBEY': True,
        'LOG_LEVEL': 'INFO',  # Change to 'DEBUG' for more verbosity
    }

    def __init__(self, num_leagues=20, *args, **kwargs):
        super(CompetitionSpider, self).__init__(*args, **kwargs)
        try:
            self.num_leagues = int(num_leagues)
            if self.num_leagues <= 0:
                raise ValueError
        except ValueError:
            self.logger.error("Invalid value for num_leagues: '%s'. Using default of 20.", num_leagues)
            self.num_leagues = 20
        self.leagues_yielded = 0

        # Comprehensive mapping of country codes to country names
        self.country_code_map = {
            'GB1': 'England',
            'ES1': 'Spain',
            'IT1': 'Italy',
            'L1': 'Germany',
            'FR1': 'France',
            'PO1': 'Portugal',
            'NL1': 'Netherlands',
            'TR1': 'Turkey',
            'BE1': 'Belgium',
            'RU1': 'Russia',
            'SER1': 'Serbia',
            'DK1': 'Denmark',
            'SE1': 'Sweden',
            'C1': 'Switzerland',
            'SC1': 'Scotland',
            'UKR1': 'Ukraine',
            'A1': 'Austria',
            'GR1': 'Greece',
            'TS1': 'Czech Republic',
            'NO1': 'Norway',
            'PL1': 'Poland',
            'KR1': 'Croatia',
            'RO1': 'Romania',
            'BU1': 'Bulgaria',
            'UNG1': 'Hungary',
            # Add more mappings as needed
        }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_competitions,
                headers={'User-Agent': self.settings.get('USER_AGENT')}
            )

    def parse_competitions(self, response):
        """
        Parse the competitions page to extract league (competition) details.
        """
        self.logger.info("Parsing competitions from %s", response.url)

        # Extract competition sections (e.g., 'Domestic leagues & cups', 'International competitions')
        competition_sections = response.xpath("//div[contains(@class, 'box')]")

        for section in competition_sections:
            # Extract competition_type from section header
            competition_type = section.xpath(".//h2/text()").get(default='Unknown').strip()
            self.logger.debug("Competition Type: %s", competition_type)

            # Extract competition rows within the section
            competition_rows = section.xpath(".//table[contains(@class, 'items')]//tbody/tr[contains(@class, 'odd') or contains(@class, 'even')]")

            for row in competition_rows:
                if self.leagues_yielded >= self.num_leagues:
                    self.logger.info("Reached the limit of %d leagues. Stopping.", self.num_leagues)
                    raise CloseSpider('limit_reached')

                # Extract competition details
                competition_name = row.xpath(".//td[2]//a/text()").get(default='').strip()
                competition_url = row.xpath(".//td[2]//a/@href").get()

                # Derive country from competition_url
                country_name = self.get_country_name(competition_url, competition_name)

                # Extract other fields
                number_of_clubs = row.xpath(".//td[3]/text()").get(default='0').strip()
                number_of_players = row.xpath(".//td[4]/text()").get(default='0').strip()
                average_age = row.xpath(".//td[5]/text()").get(default='0').strip()
                foreigners_percentage = row.xpath(".//td[contains(@class, 'zentriert')]/a/text()").get(default='0').strip()
                total_value = row.xpath(".//td[contains(@class, 'rechts') and contains(@class, 'hauptlink')]/text()").get(default='0').strip()

                # Validate competition_name
                if not competition_name:
                    self.logger.warning("Empty competition_name found. Skipping this competition.")
                    continue  # Skip to the next row without incrementing the counter

                # Debug logs to verify extraction
                self.logger.debug("Extracted total_value: '%s' for competition: '%s'", total_value, competition_name)

                # Convert numerical fields and handle potential conversion errors
                number_of_clubs = self.convert_to_int(number_of_clubs, "number_of_clubs", competition_name)
                number_of_players = self.convert_to_int(number_of_players, "number_of_players", competition_name)
                average_age = self.convert_to_float(average_age, "average_age", competition_name)
                foreigners_percentage = self.convert_to_percentage(foreigners_percentage, "foreigners_percentage", competition_name)
                total_market_value = self.convert_market_value(total_value, "total_market_value", competition_name)

                competition_data = {
                    "competition_type": competition_type,
                    "competition_name": competition_name,
                    "country": country_name,
                    "number_of_clubs": number_of_clubs,
                    "number_of_players": number_of_players,
                    "average_age": average_age,
                    "foreigners_percentage": foreigners_percentage,
                    "total_market_value": total_market_value,
                    "competition_url": response.urljoin(competition_url) if competition_url else None
                }

                self.logger.debug("Competition Data: %s", competition_data)

                yield competition_data

                self.leagues_yielded += 1
                self.logger.info("Leagues yielded: %d/%d", self.leagues_yielded, self.num_leagues)

    def get_country_name(self, competition_url, competition_name):
        """
        Derive the country name from the competition URL using the country_code_map.
        """
        if competition_url:
            match = re.search(r'/wettbewerb/([A-Z]{2,3}\d?)$', competition_url)
            if match:
                country_code = match.group(1)
                country_name = self.country_code_map.get(country_code, 'Unknown')
                if country_name == 'Unknown':
                    self.logger.warning("Country code '%s' not found in mapping for competition '%s'.", country_code, competition_name)
                return country_name
            else:
                self.logger.warning("Unable to extract country code from URL: %s for competition '%s'.", competition_url, competition_name)
                return 'Unknown'
        else:
            self.logger.warning("No competition URL found for competition: %s", competition_name)
            return 'Unknown'

    def convert_to_int(self, value, field_name, context):
        """
        Convert a string to integer, handling potential errors.
        """
        try:
            return int(value.replace(',', '').strip())
        except ValueError:
            self.logger.warning("Invalid %s '%s' for %s. Setting to None.", field_name, value, context)
            return None

    def convert_to_float(self, value, field_name, context):
        """
        Convert a string to float, handling potential errors.
        """
        try:
            return float(value.strip())
        except ValueError:
            self.logger.warning("Invalid %s '%s' for %s. Setting to None.", field_name, value, context)
            return None

    def convert_to_percentage(self, value, field_name, context):
        """
        Convert a percentage string to float, handling potential errors.
        """
        if value.endswith('%'):
            value = value.replace('%', '').strip()
        try:
            return float(value)
        except ValueError:
            self.logger.warning("Invalid %s '%s' for %s. Setting to None.", field_name, value, context)
            return None

    def convert_market_value(self, value_str, field_name, context):
        """
        Parse the market value string to a float representing millions.
        Handles values like '€11.75bn', '€5.48m', etc.
        """
        value_str = value_str.replace('€', '').strip()
        multiplier = 1

        if 'bn' in value_str:
            multiplier = 1000  # Convert billion to million
            value_str = value_str.replace('bn', '').strip()
        elif 'm' in value_str:
            value_str = value_str.replace('m', '').strip()
        elif 'k' in value_str:
            multiplier = 0.001  # Convert thousand to million
            value_str = value_str.replace('k', '').strip()

        # Remove any commas or additional characters
        value_str = re.sub(r'[^\d\.]', '', value_str)

        try:
            value_float = float(value_str)
            return value_float * multiplier
        except ValueError:
            self.logger.warning("Invalid %s '%s' for %s. Setting to None.", field_name, value_str, context)
            return None
