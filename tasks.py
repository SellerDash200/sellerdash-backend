from celery_app import celery_app
import time

@celery_app.task
def add(x, y):
    time.sleep(5)
    return x + y