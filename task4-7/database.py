import os

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_NAME"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS repositories (
            id SERIAL PRIMARY KEY,
            name TEXT,
            author TEXT,
            description TEXT,
            language TEXT,
            stars TEXT
        );
    ''')
    conn.commit()

def save_to_db(data_list):
    conn = get_connection()
    cur = conn.cursor()
    for item in data_list:
        cur.execute('''
                    INSERT INTO repositories (name, author, description, language, stars)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (item['name'], item['author'], item['description'], item['language'], item['stars']))
        conn.commit()

def get_all_from_db():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT name, author, description, language, stars FROM repositories ORDER BY stars DESC')
    return cur.fetchall()

def clear_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE repositories RESTART IDENTITY;')
    conn.commit()