import yaml
import requests
from bs4 import BeautifulSoup
import argparse
from pathlib import Path

class NewsHomeScraper:
    def __init__(self, config_path=None):
        self.config = self.load_config(config_path) if config_path else None
        self.headers = {
            'User-Agent': self.config['scraper']['user_agent'] if self.config else 'Mozilla/5.0'
        }

    def load_config(self, config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def scrape_homepage(self, url=None):
        target_url = url or self.config['scraper']['base_url']
        try:
            response = requests.get(target_url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching homepage: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Google News Homepage Scraper')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--url', type=str, help='URL to scrape')
    args = parser.parse_args()

    scraper = NewsHomeScraper(args.config)
    content = scraper.scrape_homepage(args.url)
    if content:
        print("Homepage successfully scraped")
        #print(content)
        return content
    return None

if __name__ == "__main__":
    main()