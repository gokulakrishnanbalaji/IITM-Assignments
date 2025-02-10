from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from airflow import DAG
from airflow.operators.python import PythonOperator

import time
from airflow.providers.postgres.operators.postgres import PostgresOperator
import base64
import psycopg2
from datetime import datetime

url = "https://news.google.com/"
pattern = "Top stories"

def module_1(url,ti):
    response = requests.get(url)
    ti.xcom_push(key="home_page",value=response.text)

def module_2(pattern,ti):
    response = ti.xcom_pull(key="home_page",task_ids="module_1")
    soup = BeautifulSoup(response, 'html.parser')
    
    # Find all links
    links = soup.find_all('a')
    top_stories_url = None
    
    # Search for top stories link
    for link in links:
        link_text = link.get_text().strip()
        if pattern.lower() in link_text.lower():
            href = link.get('href')
            if href:
                top_stories_url = f"https://news.google.com{href[1:-1]}"
                break
    
    ti.xcom_push(key='top_stories', value=top_stories_url)

    # if not top_stories_url:
    #     raise ValueError("Could not find top stories link")
    
    
    

def module_3(ti):
    top_stories = ti.xcom_pull(key='top_stories',task_ids="module_2")
    stories = []
    page = 1
    max_pages = 5
    
    try:
        while page <= max_pages:
            response = requests.get(f"{top_stories}&page={page}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            article_elements = soup.find_all('article')
            
            if not article_elements:
                break
            
            for article in article_elements:
                try:
                    # Extract headline and URL (unchanged)
                    headline = None
                    article_url = None
                    for a_tag in article.find_all('a'):
                        if a_tag.get_text().strip():
                            headline = a_tag.get_text().strip()
                            article_url = a_tag.get('href')
                            if article_url and not article_url.startswith('http'):
                                article_url = f"https://news.google.com{article_url[1:-1]}"
                            break
                    
                    if not headline:
                        continue
                    
                    # Extract thumbnail (unchanged)
                    thumbnail_url = None
                    figure = article.find('figure')
                    if figure:
                        img = figure.find('img')
                        if img:
                            thumbnail_url = img.get('src') or img.get('data-src')
                            if thumbnail_url and not thumbnail_url.startswith('http'):
                                thumbnail_url = f"https://news.google.com{thumbnail_url}"
                    
                    # Extract publication date
                    time_element = article.find('time')
                    publication_date = None
                    if time_element:
                        publication_date = time_element.get('datetime')
                    
                    if thumbnail_url:
                        try:
                            # Download image and encode as base64
                            image_response = requests.get(thumbnail_url)
                            image_response.raise_for_status()
                            image_data = base64.b64encode(image_response.content).decode('utf-8')
                            
                            if not any(s['headline'] == headline and s['article_url'] == article_url for s in stories):
                                stories.append({
                                    "headline": headline,
                                    "thumbnail_url": thumbnail_url,
                                    "article_url": article_url,
                                    "image_data": image_data,
                                    "publication_date": publication_date or datetime.now().isoformat()  # Use current time if no date found
                                })
                        except Exception as e:
                            continue

                        
                except Exception as e:
                    continue
            
            time.sleep(2)
            page += 1
                
        ti.xcom_push(key='story_details', value=stories)
        
    except requests.RequestException as e:
        print(f"Error fetching top stories: {e}")
        raise

def calculate_headline_similarity(headline1, headline2):
    # Convert to sets of words
    set1 = set(headline1.lower().split())
    set2 = set(headline2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0

def module_4(ti):
    stories = ti.xcom_pull(key='story_details', task_ids="module_3")
    
    conn_params = {
        "host": "host.docker.internal",
        "port": "54320",
        "database": "postgres",
        "user": "airflow",
        "password": "airflow"
    }
    
    # Add duplicate check tables
    create_tables_sql = """
    DO $$ 
    BEGIN
        -- Create news_images table if it doesn't exist
        IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'news_images') THEN
            CREATE TABLE news_images (
                image_id SERIAL PRIMARY KEY,
                image_data BYTEA NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        END IF;

        -- Create news_headlines table if it doesn't exist
        IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'news_headlines') THEN
            CREATE TABLE news_headlines (
                headline_id SERIAL PRIMARY KEY,
                image_id INTEGER REFERENCES news_images(image_id),
                headline TEXT NOT NULL,
                thumbnail_url TEXT,
                article_url TEXT,
                publication_date TIMESTAMP,
                scrape_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(headline, article_url)
            );
        END IF;
    END $$;
    """
    
    successful_inserts = 0
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        cur.execute(create_tables_sql)
        
        for story in stories:
            try:
                # Check for duplicates
                cur.execute("SELECT headline FROM news_headlines")
                existing_headlines = cur.fetchall()
                
                is_duplicate = False
                for (existing_headline,) in existing_headlines:
                    similarity = calculate_headline_similarity(story['headline'], existing_headline)
                    if similarity >= 0.85:  # Using same_day_threshold as default
                        print(f"Duplicate found - Headline: {story['headline']} - Similarity: {similarity:.2f}")
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    continue
                
                # If not duplicate, proceed with insertion
                image_response = requests.get(story['thumbnail_url'])
                image_response.raise_for_status()
                image_data = image_response.content
                
                cur.execute(
                    "INSERT INTO news_images (image_data) VALUES (%s) RETURNING image_id",
                    (psycopg2.Binary(image_data),)
                )
                image_id = cur.fetchone()[0]
                
                cur.execute("""
                    INSERT INTO news_headlines 
                    (image_id, headline, thumbnail_url, article_url, publication_date, scrape_timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (headline, article_url) DO NOTHING
                    RETURNING headline_id
                """, (
                    image_id,
                    story['headline'],
                    story['thumbnail_url'],
                    story['article_url'],
                    story['publication_date'],
                    datetime.now()
                ))
                
                if cur.fetchone() is not None:
                    successful_inserts += 1
                else:
                    cur.execute("DELETE FROM news_images WHERE image_id = %s", (image_id,))
                
            except Exception as e:
                print(f"Error processing story: {e}")
                continue
        
        conn.commit()
        
        # Status file handling
        import os
        status_dir = '/opt/airflow/dags/run'
        os.makedirs(status_dir, exist_ok=True)
        
        with open(os.path.join(status_dir, 'status'), 'w') as f:
            f.write(str(successful_inserts))
            
    except Exception as e:
        print(f"Database error: {e}")
        raise
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Define DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'news_scraping_dag_final_version',
    default_args=default_args,
    description='News Scraping Pipeline',
    schedule_interval='@hourly',  # Run every hour
    catchup=False
) as dag:
    task_1 = PythonOperator(
        task_id='module_1',
        python_callable=module_1,
        op_kwargs={'url': url},
    )
    task_2 = PythonOperator(
        task_id='module_2',
        python_callable=module_2,
        op_kwargs={'pattern': pattern},
    )
    task_3 = PythonOperator(
        task_id='module_3',
        python_callable=module_3,
    )
    task_4 = PythonOperator(
        task_id='module_4',
        python_callable=module_4,
    )

    task_1 >> task_2 >> task_3 >> task_4

