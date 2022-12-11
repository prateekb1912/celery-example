from celery import Celery
from time import sleep

app = Celery('tasks', backend='db+sqlite:///db.sqlite3', broker='amqp://')

@app.task
def reverse(text):
    sleep(5)
    return text[::-1]
