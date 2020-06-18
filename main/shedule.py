from redis import Redis
from rq_scheduler import Scheduler

scheduler = Scheduler(connection=Redis())
