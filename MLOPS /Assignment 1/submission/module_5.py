import psycopg2
from datetime import datetime
import yaml
from difflib import SequenceMatcher
import logging

class DuplicationChecker:
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
        self.logger = logging.getLogger('DuplicateChecker')

    def calculate_headline_similarity(self, headline1, headline2):
        return SequenceMatcher(None, headline1.lower(), headline2.lower()).ratio()

    def is_duplicate(self, story, same_day_threshold=0.85, different_day_threshold=0.95):
        try:
            story_date = story['publication_date'][:10]  # Extract YYYY-MM-DD
            
            # First check same day articles with lower threshold
            self.cursor.execute("""
                SELECT headline, publication_date 
                FROM news_articles
                WHERE SUBSTRING(publication_date, 1, 10) = %s
            """, (story_date,))
            
            same_day_stories = self.cursor.fetchall()
            
            for existing_headline, existing_date in same_day_stories:
                similarity = self.calculate_headline_similarity(story['headline'], existing_headline)
                if similarity >= same_day_threshold:
                    self.logger.info(f"Duplicate found - Headline: {story['headline']} - Same day duplicate found - Similarity: {similarity:.2f}")
                    return True, f"Same day duplicate found - Similarity: {similarity:.2f}"
            
            # Then check other days with higher threshold
            self.cursor.execute("""
                SELECT headline, publication_date 
                FROM news_articles
                WHERE SUBSTRING(publication_date, 1, 10) != %s
            """, (story_date,))
            
            different_day_stories = self.cursor.fetchall()
            
            for existing_headline, existing_date in different_day_stories:
                similarity = self.calculate_headline_similarity(story['headline'], existing_headline)
                if similarity >= different_day_threshold:
                    self.logger.info(f"Duplicate found - Headline: {story['headline']} - Different day duplicate found - Similarity: {similarity:.2f}")
                    return True, f"Different day duplicate found - Similarity: {similarity:.2f}"
                
            return False, "No duplicate found"
            
        except Exception as e:
            self.logger.error(f"Error checking duplication: {e}")
            return False, f"Error: {str(e)}"

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    checker = DuplicationChecker(config)
    
    test_story = {
        'headline': 'Maha Kumbh stampede LIVE updates: At least 30 dead and 60 injured, says DIG Vaibhav Krishna',
        'thumbnail_url':'ijj',
        'article_url': 'https://news.google.com/read/abc123',
        'publication_date': '2025-01-29 17:54:49'
    }
    
    is_duplicate, reason = checker.is_duplicate(test_story)
    print(f"Is duplicate: {is_duplicate}")
    print(f"Reason: {reason}")
    
    checker.close()

if __name__ == "__main__":
    main()