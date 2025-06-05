# rss-news/backend/fetcher.py
import hashlib

import feedparser
import psycopg2

from src.config import *

config = load_config()
RSS_FEEDS = config["feeds"]
DB_CONFIG = config["db"]


# Hash function to deduplicate
def hash_link(url):
    return hashlib.sha256(url.encode()).hexdigest()


def ensure_table_exists(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                link TEXT,
                description TEXT,
                pub_date TEXT,
                source TEXT,
                clicked Boolean DEFAULT false
            )
        """
        )
    conn.commit()


def insert_article(conn, article):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO articles (id, title, link, description, pub_date, source)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """,
            (
                article["id"],
                article["title"],
                article["link"],
                article["description"],
                article["pub_date"],
                article["source"],
            ),
        )
    conn.commit()


def fetch_save():
    conn = psycopg2.connect(**DB_CONFIG)

    ensure_table_exists(conn)

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:50]:
            article = {
                "id": hash_link(entry.link),
                "title": entry.title,
                "link": entry.link,
                "description": entry.get("summary", ""),
                "pub_date": entry.published,
                "source": feed.feed.title,
            }
            insert_article(conn, article)

    conn.close()


if __name__ == "__main__":
    fetch_save()
