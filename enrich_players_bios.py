import json
import requests
from bs4 import BeautifulSoup

# Function to fetch Wikipedia bio
def fetch_wikipedia_bio(name, session):
    search_url = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
    try:
        response = session.get(search_url, timeout=2)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all('p')
            for para in paragraphs:
                text = para.get_text(strip=True)
                if text:  # Only consider non-empty paragraphs
                    words = text.split()
                    return ' '.join(words[:50]) + '...' if len(words) > 50 else ' '.join(words)
        return "No wiki bio found."
    except Exception as e:
        return f"Error fetching bio: {str(e)}"

# Load players data from JSON file
input_file = "tfmkt_scraper/crawled_data/players.json"
output_file = "tfmkt_scraper/crawled_data/players_with_bios.json"

try:
    with open(input_file, "r", encoding='utf-8') as file:
        players = json.load(file)
except FileNotFoundError:
    print(f"Error: File {input_file} not found.")
    exit()

# Reuse a session for HTTP requests
session = requests.Session()

# Open output file in write mode
with open(output_file, "w", encoding='utf-8') as output_file:
    output_file.write("[\n")  # Start JSON array
    for i, player in enumerate(players):
        print(f"Fetching bio for {player['name']}...")
        player['bio'] = fetch_wikipedia_bio(player['name'], session)

        # Write each player on one line
        json_line = json.dumps(player, separators=(',', ':'), ensure_ascii=False)
        if i < len(players) - 1:
            output_file.write(json_line + ",\n")  # Add a comma if not the last entry
        else:
            output_file.write(json_line + "\n")  # No comma for the last entry

    output_file.write("]\n")  # Close JSON array

print(f"All players processed. Data saved to {output_file}.")
