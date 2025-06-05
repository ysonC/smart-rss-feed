# rss-news/frontend/app.py
import psycopg2
from flask import Flask, Response, jsonify

from config import load_config

app = Flask(__name__)
config = load_config()
DB_CONFIG = config["db"]
SITE_INFO = config["rss"]


@app.route("/rss.xml")
def rss():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        "SELECT title, link, description, pub_date, id FROM articles ORDER BY pub_date DESC LIMIT %s",
        (SITE_INFO["max_items"],),
    )
    rows = cur.fetchall()

    items = ""
    for title, link, desc, pub_date, guid in rows:
        items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <description>{desc}</description>
            <pubDate>{pub_date}</pubDate>
            <guid>{guid}</guid>
        </item>
        """

    conn.close()

    rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>{SITE_INFO["site_title"]}</title>
        <link>{SITE_INFO["site_link"]}</link>
        <description>{SITE_INFO["site_description"]}</description>
        {items}
    </channel>
    </rss>"""

    return Response(rss_feed, mimetype="application/rss+xml")


@app.route("/api/news")
def get_latest_news():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        "SELECT title, link, description, pub_date FROM articles ORDER BY pub_date DESC LIMIT 10"
    )
    rows = cur.fetchall()
    conn.close()

    news_list = [
        {"title": title, "link": link, "description": desc, "pub_date": pub_date}
        for title, link, desc, pub_date in rows
    ]

    return jsonify(news_list)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
