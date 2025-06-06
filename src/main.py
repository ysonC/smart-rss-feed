import logging
import threading
import time

import psycopg2
from flask import Flask, Response, jsonify

from config import load_config
from fetcher import fetch_save

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)
config = load_config()
DB_CONFIG = config["db"]
SITE_INFO = config["rss"]


@app.route("/rss.xml")
def rss():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(
            "SELECT title, link, description, pub_date, id FROM articles ORDER BY pub_date DESC LIMIT %s",
            (SITE_INFO["max_items"],),
        )
        rows = cur.fetchall()
        conn.close()

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

    except Exception:
        logging.exception("Error generating RSS feed")
        return Response("Internal Server Error", status=500)


@app.route("/api/news")
def get_latest_news():
    try:
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

    except Exception:
        logging.exception("Error fetching latest news")
        return jsonify({"error": "Internal Server Error"}), 500


def start_background_fetcher(interval_seconds=600):
    def run_loop():
        while True:
            try:
                logging.info("Running fetcher...")
                fetch_save()
                logging.info("Fetcher completed successfully.")
            except Exception:
                logging.exception("Fetcher failed")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()


if __name__ == "__main__":
    logging.info("Starting Flask app with background fetcher...")
    start_background_fetcher(interval_seconds=600)
    app.run(host="0.0.0.0", port=8080)
