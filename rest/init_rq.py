from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

def init_redis_components(app):
    redis_conn = Redis.from_url(app.config['REDIS_URL'])
    app.queue = Queue(connection=redis_conn)
    app.scheduler = Scheduler(queue=app.queue, connection=redis_conn)