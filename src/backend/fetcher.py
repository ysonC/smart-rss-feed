# rss-news/backend/fetcher.py
import hashlib
from datetime import datetime

import feedparser
import psycopg2

RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]

DB_CONFIG = {
    "host": "rss-db.ysonsbaolab.dev",
    "port": "32005",
    "database": "rss",
    "user": "admin",
    "password": "password",
}


# Hash function to deduplicate
def hash_link(url):
    return hashlib.sha256(url.encode()).hexdigest()


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


def main():
    conn = psycopg2.connect(**DB_CONFIG)

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            article = {
                "id": hash_link(entry.link),
                "title": entry.title,
                "link": entry.link,
                "description": entry.get("summary", ""),
                "pub_date": entry.published,
                "source": feed.feed.title,
            }
            insert_article(conn, article)
    print(article)

    conn.close()


if __name__ == "__main__":
    main()
