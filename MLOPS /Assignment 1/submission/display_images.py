import psycopg2
import yaml

def save_top_images():
    n=int(input('Number of images you want to retrieve from database as jpg: '))
    # Load database configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        db_config = config['database']

    # Connect to database
    conn = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )
    
    try:
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT i.image_data 
            FROM news_images i 
            JOIN news_articles a ON i.article_id = a.id 
            LIMIT {n}
        """)
        
        results = cursor.fetchall()
        
        for idx, (image_data,) in enumerate(results, 1):
            image_filename = f"news_image_{idx}.jpg"
            with open(image_filename, 'wb') as f:
                f.write(image_data)
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    save_top_images()