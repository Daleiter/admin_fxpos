import os
from redis import Redis
from rq import Worker, Queue, Connection
from views.app_all import app

listen = ['default']

if __name__ == '__main__':
    with app.app_context():
        redis_conn = Redis.from_url(app.config['REDIS_URL'])
        with Connection(redis_conn):
            worker = Worker(map(Queue, listen))
            worker.work()