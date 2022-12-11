from celery import Celery
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from celery.schedules import crontab

app = Celery('tasks', backend='db+sqlite:///db.sqlite3', broker='amqp://')

app.conf.beat_schedule = {
    'scraping-task': {
        'task': 'tasks.scrape_rss_news',
        'schedule': crontab()
    }
}

@app.task
def save_data(articles_list):
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')    
    filename = 'articles-{}.json'.format(timestamp)    
    
    with open(filename, mode='w') as outFile:
        json.dump(articles_list, outFile)

@app.task
def scrape_rss_news():
    articles_list = []

    try:
        r = requests.get("https://news.ycombinator.com/rss")
        soup = BeautifulSoup(r.content, features='xml')

        articles = soup.findAll('item')

        for article in articles:
            title = article.find('title').text
            link = article.find('link').text
            pubDate = article.find('pubDate').text

            articles_list.append(
                {
                    'title': title,
                    'link': link,
                    'published': pubDate
                }
            )

        return save_data(articles_list)

    except Exception as e:
        print(f"Job failed: {e}")
