import feedparser
from flask import Flask, Response

app = Flask(__name__)

# RSS feeds to aggregate
RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]


@app.route("/rss")
def aggregated_rss():
    items = ""
    for feed_url in RSS_FEEDS:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries[:5]:  # Get top 5 per feed
            items += f"""
            <item>
                <title>{entry.title}</title>
                <link>{entry.link}</link>
                <description>{entry.get('summary', '')}</description>
                <pubDate>{entry.published}</pubDate>
                <guid>{entry.link}</guid>
            </item>
            """

    rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
      <channel>
        <title>My Aggregated Feed</title>
        <link>https://yourdomain.com/rss.xml</link>
        <description>News from multiple sources</description>
        {items}
      </channel>
    </rss>"""

    return Response(rss_feed, mimetype="application/rss+xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
