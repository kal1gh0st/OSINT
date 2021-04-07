import requests
import urllib
import json

google_news_section = "https://news.google.com/news?q=hockey&pz=1&cf=all&ned=ca&hl=en&output=rss"
google_news_url = "http://ajax.googleapis.com/ajax/services/feed/load?v=1.0&q=%s" % urllib.quote(google_news_section)

# send off the request
response = requests.get(google_news_url)

if response.status_code == 200:
    
    news = json.loads(response.content)
    
    for article in news['responseData']['feed']['entries']:
        print "%s - %s - %s" % (article['publishedDate'],article['title'],article['link'])    