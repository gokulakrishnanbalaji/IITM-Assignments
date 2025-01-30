import psycopg2
from datetime import datetime
import requests
import yaml
import logging
from module_3 import StoryExtractor
from module_2 import TopStoriesScraper
from module_1 import NewsHomeScraper
from module_5 import DuplicationChecker

class NewsDatabase:
    def __init__(self, config):
        self.db_config = config['database']
        self.conn = psycopg2.connect(
            dbname=self.db_config['dbname'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            host=self.db_config['host'],
            port=self.db_config['port']
        )
        self.cursor = self.conn.cursor()
        
        # Setup logging
        logging.basicConfig(
            filename='duplicates.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger('DuplicateChecker')
        self.duplicate_checker = DuplicationChecker(config)

    def store_article(self, story):
        try:
            # Check for duplicates first
            is_duplicate, reason = self.duplicate_checker.is_duplicate(story)
            
            if is_duplicate:
                self.logger.info(f"Duplicate found - Headline: {story['headline']} - {reason}")
                return False

            # Insert article data if not duplicate
            self.cursor.execute("""
                INSERT INTO news_articles (headline, article_url, publication_date)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (story['headline'], story['article_url'], story['publication_date']))
            
            article_id = self.cursor.fetchone()[0]
            
            # Store image if exists
            if story['thumbnail_url']:
                try:
                    response = requests.get(story['thumbnail_url'])
                    image_data = response.content
                    
                    self.cursor.execute("""
                        INSERT INTO news_images (article_id, thumbnail_url, image_data)
                        VALUES (%s, %s, %s)
                    """, (article_id, story['thumbnail_url'], psycopg2.Binary(image_data)))
                except Exception as e:
                    self.logger.error(f"Error downloading image: {e}")
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error storing article: {e}")
            return False

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            if hasattr(self, 'duplicate_checker'):
                self.duplicate_checker.close()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Get stories using previous modules
    home_scraper = NewsHomeScraper('config.yaml')
    homepage_content = home_scraper.scrape_homepage()
    
    if homepage_content:
        top_stories_scraper = TopStoriesScraper(homepage_content, config)
        top_stories_url = top_stories_scraper.find_top_stories_link()
        
        if top_stories_url:
            story_extractor = StoryExtractor(config)
            stories = story_extractor.extract_stories(top_stories_url)
            
            if stories:
                # Store in database
                db = NewsDatabase(config)
                stored_count = 0
                skipped_count = 0
                
                for story in stories:
                    if db.store_article(story):
                        stored_count += 1
                    else:
                        skipped_count += 1
                
                db.close()
                db.logger.info(f"Successfully stored {stored_count} articles in database")
                db.logger.info(f"Skipped {skipped_count} articles")
            else:
                logging.info("No stories were found")
        else:
            logging.info("Could not find top stories link")

if __name__ == "__main__":
    main()