import logging
from datetime import datetime
import yaml
import sys
import traceback
import time
from module_1 import NewsHomeScraper
from module_2 import TopStoriesScraper
from module_3 import StoryExtractor
from module_4 import NewsDatabase

def setup_logging():
    logging.basicConfig(
        filename='pipeline.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)

def run_pipeline(config):
    try:
        start_time = datetime.now()
        logging.info("Starting news pipeline execution")
        
        # Module 1: Scrape homepage
        home_scraper = NewsHomeScraper('config.yaml')
        homepage_content = home_scraper.scrape_homepage()
        if not homepage_content:
            raise Exception("Failed to scrape homepage")
        
        # Module 2: Extract top stories link
        top_stories_scraper = TopStoriesScraper(homepage_content, config)
        top_stories_url = top_stories_scraper.find_top_stories_link()
        if not top_stories_url:
            raise Exception("Failed to find top stories link")
        
        # Module 3: Extract stories
        story_extractor = StoryExtractor(config)
        stories = story_extractor.extract_stories(top_stories_url)
        if not stories:
            raise Exception("No stories were extracted")
        
        # Module 4: Store in database
        db = NewsDatabase(config)
        stored_count = 0
        skipped_count = 0
        
        for story in stories:
            if db.store_article(story):
                stored_count += 1
            else:
                skipped_count += 1
        
        db.close()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logging.info(f"Pipeline completed. Stored: {stored_count}, Skipped: {skipped_count}, Duration: {duration:.2f}s")
        return True
        
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def main():
    setup_logging()
    
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        frequency = config.get('pipeline', {}).get('frequency', 3600)  # Default: 1 hour in seconds
        
        while True:
            run_pipeline(config)
            logging.info(f"Waiting {frequency} seconds until next run...")
            time.sleep(frequency)
            
    except KeyboardInterrupt:
        logging.info("Pipeline stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()