from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import psycopg2
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from airflow.sensors.external_task import ExternalTaskSensor

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "gokulbalaji2408@gmail.com"
APP_PASSWORD = "change this with your email token(16 digit), mine works"  
RECIPIENT_EMAIL = "gokulbalaji2408@gmail.com"

def send_email(message):
    """Send email using SMTP with App Password"""
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)  # Using App Password here
            server.send_message(message)
            print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise

def get_previous_state():
    """Load previous database state from JSON file"""
    try:
        with open('/opt/airflow/dags/previous_state.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'last_headline_id': 0}

def save_current_state(state):
    """Save current database state to JSON file"""
    with open('/opt/airflow/dags/previous_state.json', 'w') as f:
        json.dump(state, f)

def prepare_email_content(new_entries):
    """Create email content from new entries"""
    message = MIMEMultipart()
    message["Subject"] = f"New Articles Alert: {len(new_entries)} new entries"
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL

    content = "New articles have been added:\n\n"
    for entry in new_entries:
        content += f"• {entry['headline']}\n"
        if entry.get('publication_date'):
            content += f"  Published: {entry['publication_date']}\n"
        content += f"  URL: {entry['article_url']}\n\n"

    message.attach(MIMEText(content, "plain"))
    return message

def check_and_notify(**context):
    """Main function to check for new entries and send notification"""
    conn_params = {
        "host": "host.docker.internal",
        "port": "54320",
        "database": "postgres",
        "user": "airflow",
        "password": "airflow"
    }
    
    try:
        # Get previous state
        prev_state = get_previous_state()
        last_headline_id = prev_state['last_headline_id']
        
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # Get new entries
        cur.execute("""
            SELECT h.headline_id, h.headline, h.article_url, h.publication_date
            FROM news_headlines h
            WHERE h.headline_id > %s
            ORDER BY h.headline_id
        """, (last_headline_id,))
        
        new_entries = []
        max_headline_id = last_headline_id
        
        for row in cur.fetchall():
            headline_id, headline, article_url, pub_date = row
            max_headline_id = max(max_headline_id, headline_id)
            new_entries.append({
                'headline': headline,
                'article_url': article_url,
                'publication_date': pub_date.isoformat() if pub_date else None
            })
        
        if new_entries:
            # Prepare and send email
            message = prepare_email_content(new_entries)
            send_email(message)
            
            # Update state
            save_current_state({'last_headline_id': max_headline_id})
            
        # Clean up status file
        os.remove('/opt/airflow/dags/run/status')
            
    except Exception as e:
        print(f"Error in check_and_notify: {e}")
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

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
    'news_email_notification_dag_final_version',
    default_args=default_args,
    description='Send email notifications for new articles',
    schedule_interval='@hourly',  # Match DAG1's schedule
    catchup=False
) as dag:
    
    # Wait for DAG1 to complete
    wait_for_dag1 = ExternalTaskSensor(
        task_id='wait_for_scraping',
        external_dag_id='news_scraping_dag_final_version',
        external_task_id='module_4',  # Wait for the last task of DAG1
        timeout=600,
        poke_interval=60,
    )
    
    # Wait for status file
    wait_for_status = FileSensor(
        task_id='wait_for_status_file',
        fs_conn_id='file',  # Use 'file' as connection ID
        filepath='/opt/airflow/dags/run/status',
        poke_interval=30,
        timeout=600,
    )
    
    # Process new entries and send email
    notify_task = PythonOperator(
        task_id='check_and_notify',
        python_callable=check_and_notify,
        provide_context=True,
    )
    
    wait_for_dag1 >> wait_for_status >> notify_task