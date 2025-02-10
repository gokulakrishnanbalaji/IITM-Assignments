import requests
from bs4 import BeautifulSoup
import yaml
import argparse
from module_2 import TopStoriesScraper
from module_1 import NewsHomeScraper
import time
import json
from datetime import datetime, timedelta

class StoryExtractor:
    def __init__(self, config):
        self.config = config
        self.headers = {
            'User-Agent': config['scraper']['user_agent']
        }

    def extract_stories(self, url, max_retries=3):
        stories = []
        page = 1
        
        while page <= max_retries:
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                articles = soup.find_all('article')
                
                for article in articles:
                    story = self._extract_story_data(article)
                    if story and story not in stories:
                        stories.append(story)
                
                if not articles or len(articles) == 0:
                    break
                
                page += 1
                time.sleep(2)
                
            except requests.RequestException as e:
                print(f"Error fetching page {page}: {e}")
                break
                
        return stories

    def _convert_relative_time(self, relative_time):
        try:
            now = datetime.now()
            
            if 'minute' in relative_time or 'minutes' in relative_time:
                minutes = int(relative_time.split()[0])
                return (now - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
            
            elif 'hour' in relative_time or 'hours' in relative_time:
                hours = int(relative_time.split()[0])
                return (now - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
            
            elif 'day' in relative_time or 'days' in relative_time:
                days = int(relative_time.split()[0])
                return (now - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            
            elif 'Yesterday' in relative_time:
                return (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            
            else:
                return now.strftime("%Y-%m-%d %H:%M:%S")
                
        except Exception:
            return now.strftime("%Y-%m-%d %H:%M:%S")

    def _extract_story_data(self, article):
        try:
            # Extract headline and URL first
            headline = None
            for a_tag in article.find_all('a'):
                if a_tag.get_text().strip():
                    headline = a_tag.get_text().strip()
                    article_url = a_tag.get('href')
                    if article_url and not article_url.startswith('http'):
                        article_url = f"https://news.google.com{article_url[1:-1]}"
                    break
            
            if not headline:
                return None
            
            # Extract thumbnail
            thumbnail_url = None
            # Try figure tag first
            figure = article.find('figure')
            if figure:
                img = figure.find('img')
                if img:
                    thumbnail_url = img.get('src') or img.get('data-src')
                    thumbnail_url = f"https://news.google.com{thumbnail_url}"
            
            # If no image found, skip this story
            if not thumbnail_url:
                return None
            
            # Extract and convert publication date
            time_elem = article.find('time')
            relative_time = time_elem.get_text().strip() if time_elem else None
            pub_date = self._convert_relative_time(relative_time) if relative_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                'headline': headline,
                'thumbnail_url': thumbnail_url,
                'article_url': article_url,
                'publication_date': pub_date
            }
            
        except Exception as e:
            print(f"Error extracting story data: {e}")
            return None

    def save_stories(self, stories, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stories, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description='Google News Story Extractor')
    parser.add_argument('--config', type=str, required=True, help='Path to config file')
    parser.add_argument('--output', type=str, default='stories.json', help='Output file path')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    home_scraper = NewsHomeScraper(args.config)
    homepage_content = home_scraper.scrape_homepage()
    
    if homepage_content:
        top_stories_scraper = TopStoriesScraper(homepage_content, config)
        top_stories_url = top_stories_scraper.find_top_stories_link()
        
        if top_stories_url:
            extractor = StoryExtractor(config)
            stories = extractor.extract_stories(top_stories_url)
            if stories:
                extractor.save_stories(stories, args.output)
                print(f"Successfully extracted {len(stories)} stories to {args.output}")
            else:
                print("No stories were found")
        else:
            print("Could not find top stories link")

if __name__ == "__main__":
    main()