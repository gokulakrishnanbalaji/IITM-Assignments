from bs4 import BeautifulSoup
import argparse
import yaml
from module_1 import NewsHomeScraper

class TopStoriesScraper:
    def __init__(self, html_content, config):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.config = config

    def find_top_stories_link(self):
        pattern = self.config['scraper']['top_stories_pattern']
        links = self.soup.find_all('a')
        
        for link in links:
            link_text = link.get_text().strip()
            if pattern.lower() in link_text.lower():
                href = link.get('href')
                if href:
                    return f"https://news.google.com{href[1:-1]}"
        return None

def main():
    parser = argparse.ArgumentParser(description='Google News Top Stories Scraper')
    parser.add_argument('--config', type=str, help='Path to config file')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    home_scraper = NewsHomeScraper(args.config)
    homepage_content = home_scraper.scrape_homepage()
    
    if homepage_content:
        
        top_stories_scraper = TopStoriesScraper(homepage_content, config)
        top_stories_link = top_stories_scraper.find_top_stories_link()
        if top_stories_link:
            print(f"Found top stories link: {top_stories_link}")
            return top_stories_link
    
    print("Could not find top stories link")
    return None

if __name__ == "__main__":
    main()